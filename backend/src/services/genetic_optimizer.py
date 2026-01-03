"""
Genetic Algorithm Optimizer - Main AI Optimization Engine
Uses PyGAD library to evolve optimal house layouts.

The genetic algorithm evolves populations of house layouts over multiple
generations, selecting the best designs based on the fitness function.
"""

import time
from typing import Dict, Any, Callable, Optional, List
import numpy as np
import pygad
from loguru import logger

from ..models.schemas import (
    LandInputSchema,
    LayoutOutputSchema,
    RoomSchema
)
from ..config.settings import settings
from .fitness_evaluator import FitnessEvaluator
from .room_optimizer import RoomOptimizer
from .room_placer import SmartRoomPlacer
from .architectural_layout import ArchitecturalLayoutGenerator


class GeneticOptimizer:
    """
    Genetic Algorithm optimizer for house layout generation.

    Uses PyGAD to evolve optimal room arrangements based on
    multi-objective fitness evaluation.
    """

    def __init__(
        self,
        land_input: LandInputSchema,
        generations: Optional[int] = None,
        population_size: Optional[int] = None,
        mutation_rate: Optional[float] = None,
        crossover_rate: Optional[float] = None,
    ):
        """
        Initialize genetic algorithm optimizer.

        Args:
            land_input: Land dimensions and requirements
            generations: Number of generations (default from settings)
            population_size: Population size (default from settings)
            mutation_rate: Mutation probability (default from settings)
            crossover_rate: Crossover probability (default from settings)
        """
        # STEP 1: Intelligent room optimization
        # Check if requested rooms fit, reduce if necessary
        logger.info("=== INTELLIGENT ROOM OPTIMIZATION ===")
        room_optimizer = RoomOptimizer(land_input)
        self.optimized_land_input, self.optimization_messages = room_optimizer.optimize_room_count()

        # Log optimization results
        for msg in self.optimization_messages:
            logger.info(msg)

        # Use optimized input for genetic algorithm
        self.land_input = self.optimized_land_input
        self.original_land_input = land_input  # Keep original for reference

        # GA parameters (use provided or default from settings)
        self.generations = generations or settings.GA_GENERATIONS
        self.population_size = population_size or settings.GA_POPULATION_SIZE
        self.mutation_rate = mutation_rate or settings.GA_MUTATION_RATE
        self.crossover_rate = crossover_rate or settings.GA_CROSSOVER_RATE
        self.tournament_size = settings.GA_TOURNAMENT_SIZE

        # Initialize fitness evaluator with optimized input
        self.fitness_evaluator = FitnessEvaluator(self.land_input)

        # Gene space (all genes are 0-1 continuous values)
        self.num_genes = self.fitness_evaluator.chromosome_length
        self.gene_space = [
            {'low': 0.0, 'high': 1.0} for _ in range(self.num_genes)
        ]

        # Tracking
        self.best_fitness_per_generation = []
        self.start_time = None
        self.end_time = None
        self.ga_instance = None

        # Initialize smart room placer for better initial population
        self.room_placer = SmartRoomPlacer(
            buildable=self.fitness_evaluator.buildable,
            required_rooms=self.fitness_evaluator.required_rooms
        )

        logger.info(
            f"Genetic Optimizer initialized: "
            f"{self.generations} generations, "
            f"population: {self.population_size}, "
            f"mutation: {self.mutation_rate}, "
            f"genes: {self.num_genes}"
        )

    def _generate_smart_initial_population(self, num_solutions: int) -> List[List[float]]:
        """
        Generate initial population with non-overlapping layouts.

        Args:
            num_solutions: Number of solutions to generate

        Returns:
            List of chromosomes (each is a list of genes)
        """
        logger.info(f"Generating {num_solutions} non-overlapping initial layouts...")

        population = []

        for i in range(num_solutions):
            # Generate non-overlapping layout using smart placer
            method = ["grid", "sequential"][i % 2]  # Alternate methods for diversity
            rooms = self.room_placer.generate_non_overlapping_layout(method=method)

            # Encode rooms into chromosome
            chromosome = self._encode_rooms_to_chromosome(rooms)
            population.append(chromosome)

            if (i + 1) % 10 == 0:
                logger.debug(f"Generated {i+1}/{num_solutions} initial solutions")

        logger.info(f"Initial population generated: {len(population)} non-overlapping layouts")
        return population

    def _encode_rooms_to_chromosome(self, rooms: List[RoomSchema]) -> List[float]:
        """
        Encode room layout into chromosome (gene values).

        Args:
            rooms: List of rooms

        Returns:
            Chromosome (list of 0-1 values)
        """
        chromosome = []
        buildable_width = self.fitness_evaluator.buildable['width']
        buildable_length = self.fitness_evaluator.buildable['length']
        offset_x = self.fitness_evaluator.buildable['offset_x']
        offset_y = self.fitness_evaluator.buildable['offset_y']

        for room in rooms:
            # Encode position as ratio
            max_x = max(0.001, buildable_width - room.width)
            max_y = max(0.001, buildable_length - room.height)

            x_ratio = (room.x - offset_x) / max_x if max_x > 0 else 0.5
            y_ratio = (room.y - offset_y) / max_y if max_y > 0 else 0.5

            # Encode size as ratio
            w_ratio = room.width / buildable_width if buildable_width > 0 else 0.2
            h_ratio = room.height / buildable_length if buildable_length > 0 else 0.2

            # Clamp to 0-1 range
            x_ratio = max(0.0, min(1.0, x_ratio))
            y_ratio = max(0.0, min(1.0, y_ratio))
            w_ratio = max(0.05, min(0.5, w_ratio))
            h_ratio = max(0.05, min(0.5, h_ratio))

            chromosome.extend([x_ratio, y_ratio, w_ratio, h_ratio])

        # Pad if needed
        while len(chromosome) < self.num_genes:
            chromosome.append(0.5)

        return chromosome[:self.num_genes]

    def optimize(
        self,
        progress_callback: Optional[Callable[[int, float], None]] = None
    ) -> LayoutOutputSchema:
        """
        Run genetic algorithm optimization to find best house layout.

        Args:
            progress_callback: Optional callback function(generation, best_fitness)
                called after each generation

        Returns:
            LayoutOutputSchema with optimized layout and scores
        """
        logger.info("Starting genetic algorithm optimization...")
        self.start_time = time.time()

        # Create callback wrapper for progress tracking
        def on_generation(ga_instance):
            generation = ga_instance.generations_completed
            best_fitness = ga_instance.best_solution()[1]

            self.best_fitness_per_generation.append(best_fitness)

            logger.info(
                f"Generation {generation}/{self.generations}: "
                f"Best fitness = {best_fitness:.2f}"
            )

            # Call user progress callback if provided
            if progress_callback:
                try:
                    progress_callback(generation, best_fitness)
                except Exception as e:
                    logger.warning(f"Progress callback error: {e}")

        # Generate smart initial population (non-overlapping layouts)
        initial_population = self._generate_smart_initial_population(self.population_size)

        # Configure PyGAD instance with smart initial population
        self.ga_instance = pygad.GA(
            num_generations=self.generations,
            num_parents_mating=max(2, self.population_size // 4),
            fitness_func=self.fitness_evaluator.evaluate_fitness,
            sol_per_pop=self.population_size,
            num_genes=self.num_genes,
            initial_population=np.array(initial_population),  # Use smart initial population!
            gene_type=float,

            # Selection
            parent_selection_type="tournament",
            K_tournament=self.tournament_size,

            # Crossover
            crossover_type="two_points",
            crossover_probability=self.crossover_rate,

            # Mutation
            mutation_type="random",
            mutation_probability=self.mutation_rate,
            mutation_percent_genes=20,  # Mutate 20% of genes when mutation occurs

            # Elitism - keep best solutions
            keep_elitism=max(1, self.population_size // 10),

            # Callbacks
            on_generation=on_generation,

            # Prevent duplicate solutions
            allow_duplicate_genes=True,  # Genes can have same values
            suppress_warnings=True,
        )

        logger.info("Running genetic algorithm evolution...")

        # Run evolution
        try:
            self.ga_instance.run()
        except Exception as e:
            logger.error(f"Genetic algorithm error: {e}")
            raise

        self.end_time = time.time()
        elapsed_time = self.end_time - self.start_time

        # Get best solution
        best_solution, best_fitness, _ = self.ga_instance.best_solution()

        logger.info(
            f"Optimization complete in {elapsed_time:.2f}s: "
            f"Best fitness = {best_fitness:.2f}"
        )

        # Decode best solution to rooms
        best_rooms = self.fitness_evaluator.decode_chromosome(best_solution)

        # Get detailed scores
        detailed_scores = self.fitness_evaluator.get_detailed_scores(best_solution)

        # Calculate total built area and coverage
        total_built_area = sum(room.area for room in best_rooms)
        total_area = self.land_input.total_area or (self.land_input.length * self.land_input.width)
        coverage_percentage = (total_built_area / total_area) * 100 if total_area else 0

        # Generate complete architectural layout with walls, doors, corridors, fixtures
        logger.info("Generating architectural floor plan with corridors, walls, doors, and fixtures...")
        architectural_layout = self._generate_architectural_layout(best_rooms)

        # Create output schema with optimization messages
        layout_output = LayoutOutputSchema(
            rooms=best_rooms,
            fitness_score=detailed_scores['fitness_score'],
            efficiency_score=detailed_scores['space_efficiency'],
            sunlight_score=detailed_scores['sunlight_score'],
            privacy_score=detailed_scores['privacy_score'],
            regulation_compliance=detailed_scores['regulation_compliance'],
            total_built_area=total_built_area,
            coverage_percentage=coverage_percentage,
            generation_time_seconds=elapsed_time,
            optimization_messages=self.optimization_messages,
        )

        # Add architectural elements to output (using __dict__ to bypass Pydantic validation)
        layout_output.__dict__['architectural_elements'] = architectural_layout

        logger.info(
            f"Architectural layout complete: "
            f"{len(architectural_layout['walls'])} walls, "
            f"{len(architectural_layout['doors'])} doors, "
            f"{len(architectural_layout['corridors'])} corridors, "
            f"{len(architectural_layout['fixtures'])} fixtures"
        )

        return layout_output

    def _generate_architectural_layout(self, rooms: List[RoomSchema]) -> Dict[str, Any]:
        """
        Generate complete architectural layout with walls, doors, corridors, and fixtures.

        Args:
            rooms: List of optimized room placements from GA

        Returns:
            Dictionary with architectural elements (walls, doors, corridors, fixtures)
        """
        # Create architectural layout generator
        generator = ArchitecturalLayoutGenerator(
            buildable=self.fitness_evaluator.buildable,
            land_input=self.land_input
        )

        # Generate complete architectural layout
        # Note: The generator creates its own room placements based on Vastu principles
        # We use the GA-optimized rooms as a reference but regenerate for architectural accuracy
        layout = generator.generate_layout()

        return layout

    def get_optimization_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the optimization process.

        Returns:
            Dictionary with optimization statistics
        """
        if not self.ga_instance:
            return {'error': 'Optimization not run yet'}

        if not self.start_time or not self.end_time:
            return {'error': 'Optimization incomplete'}

        best_solution, best_fitness, best_idx = self.ga_instance.best_solution()

        return {
            'total_generations': self.generations,
            'population_size': self.population_size,
            'best_fitness': float(best_fitness),
            'best_solution_index': int(best_idx),
            'optimization_time': self.end_time - self.start_time,
            'fitness_history': self.best_fitness_per_generation,
            'improvement': (
                self.best_fitness_per_generation[-1] - self.best_fitness_per_generation[0]
                if len(self.best_fitness_per_generation) > 1
                else 0.0
            ),
            'convergence_rate': self._calculate_convergence_rate(),
        }

    def _calculate_convergence_rate(self) -> float:
        """
        Calculate how quickly the algorithm converged.

        Returns:
            Convergence rate (0-1, higher = faster convergence)
        """
        if len(self.best_fitness_per_generation) < 2:
            return 0.0

        # Check how early the best fitness was found
        best_fitness = max(self.best_fitness_per_generation)
        first_best_gen = self.best_fitness_per_generation.index(best_fitness)

        # Normalize (earlier = higher convergence rate)
        convergence_rate = 1.0 - (first_best_gen / len(self.best_fitness_per_generation))

        return convergence_rate

    def get_best_solution_details(self) -> Dict[str, Any]:
        """
        Get detailed information about the best solution.

        Returns:
            Dictionary with best solution details
        """
        if not self.ga_instance:
            return {'error': 'Optimization not run yet'}

        best_solution, best_fitness, _ = self.ga_instance.best_solution()

        # Get detailed scores and rooms
        detailed_scores = self.fitness_evaluator.get_detailed_scores(best_solution)

        return {
            'fitness_score': best_fitness,
            'chromosome': best_solution.tolist(),
            'detailed_scores': {
                'space_efficiency': detailed_scores['space_efficiency'],
                'sunlight_score': detailed_scores['sunlight_score'],
                'privacy_score': detailed_scores['privacy_score'],
                'circulation_score': detailed_scores['circulation_score'],
                'regulation_compliance': detailed_scores['regulation_compliance'],
            },
            'rooms': detailed_scores['rooms'],
            'total_room_area': sum(r['area'] for r in detailed_scores['rooms']),
            'buildable_area': self.fitness_evaluator.buildable['area'],
            'coverage_ratio': (
                sum(r['area'] for r in detailed_scores['rooms']) /
                self.fitness_evaluator.buildable['area']
            ),
        }

    def optimize_batch(
        self,
        num_runs: int = 3,
        progress_callback: Optional[Callable[[int, int, float], None]] = None
    ) -> LayoutOutputSchema:
        """
        Run optimization multiple times and return the best result.

        Useful for ensuring we find the global optimum, not just local optimum.

        Args:
            num_runs: Number of independent optimization runs
            progress_callback: Optional callback(run_number, generation, fitness)

        Returns:
            Best layout from all runs
        """
        logger.info(f"Running batch optimization with {num_runs} independent runs...")

        best_overall_layout = None
        best_overall_fitness = 0.0

        for run in range(1, num_runs + 1):
            logger.info(f"--- Optimization Run {run}/{num_runs} ---")

            # Create callback wrapper that includes run number
            if progress_callback:
                def run_callback(gen, fitness):
                    progress_callback(run, gen, fitness)
            else:
                run_callback = None

            # Run optimization
            layout = self.optimize(progress_callback=run_callback)

            # Check if this is the best so far
            if layout.fitness_score > best_overall_fitness:
                best_overall_fitness = layout.fitness_score
                best_overall_layout = layout
                logger.info(f"New best fitness: {best_overall_fitness:.2f}")

        logger.info(
            f"Batch optimization complete. "
            f"Best overall fitness: {best_overall_fitness:.2f}"
        )

        return best_overall_layout

    def get_population_diversity(self) -> float:
        """
        Calculate diversity of current population.

        Returns:
            Diversity score (0-1, higher = more diverse)
        """
        if not self.ga_instance or not hasattr(self.ga_instance, 'population'):
            return 0.0

        population = self.ga_instance.population

        # Calculate average pairwise distance
        distances = []
        for i in range(len(population)):
            for j in range(i + 1, len(population)):
                distance = np.linalg.norm(population[i] - population[j])
                distances.append(distance)

        if not distances:
            return 0.0

        # Normalize by maximum possible distance
        max_distance = np.sqrt(self.num_genes)  # Max distance in [0,1]^n space
        avg_distance = np.mean(distances)

        diversity = avg_distance / max_distance if max_distance > 0 else 0.0

        return min(1.0, diversity)

    def save_optimization_plot(self, filename: str = "fitness_evolution.png"):
        """
        Save plot of fitness evolution over generations.

        Args:
            filename: Output filename
        """
        try:
            import matplotlib.pyplot as plt

            plt.figure(figsize=(10, 6))
            plt.plot(
                range(1, len(self.best_fitness_per_generation) + 1),
                self.best_fitness_per_generation,
                marker='o',
                linestyle='-',
                linewidth=2,
                markersize=4
            )
            plt.xlabel('Generation', fontsize=12)
            plt.ylabel('Best Fitness Score', fontsize=12)
            plt.title(
                'Genetic Algorithm Fitness Evolution\n'
                f'Final Fitness: {self.best_fitness_per_generation[-1]:.2f}',
                fontsize=14
            )
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close()

            logger.info(f"Fitness evolution plot saved: {filename}")

        except Exception as e:
            logger.error(f"Error saving plot: {e}")


# Convenience function for quick optimization
def optimize_land_layout(
    land_input: LandInputSchema,
    generations: int = 100,
    population_size: int = 50,
    **kwargs
) -> LayoutOutputSchema:
    """
    Quick convenience function to optimize a land layout.

    Args:
        land_input: Land dimensions and requirements
        generations: Number of GA generations
        population_size: Population size
        **kwargs: Additional optimizer parameters

    Returns:
        Optimized layout
    """
    optimizer = GeneticOptimizer(
        land_input=land_input,
        generations=generations,
        population_size=population_size,
        **kwargs
    )

    return optimizer.optimize()
