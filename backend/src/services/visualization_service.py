"""
Visualization Service - Generate Floor Plan Images
Creates professional PNG images of house layouts with colors, labels, and dimensions.
"""

import os
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, FancyBboxPatch
from matplotlib.lines import Line2D
import numpy as np
from loguru import logger

from ..models.schemas import LandInputSchema, RoomSchema, LayoutOutputSchema
from .building_rules import SriLankanBuildingRules


class VisualizationService:
    """
    Service for generating visual representations of house layouts.
    Creates professional floor plan images with colors, labels, and dimensions.
    """

    # Room type colors (professional, high-contrast color scheme)
    ROOM_COLORS = {
        'bedroom': '#B8E6D5',           # Mint green
        'master_bedroom': '#6FA8DC',    # Sky blue
        'toilet': '#FFB3D9',            # Bright pink
        'kitchen': '#FFE599',           # Bright yellow
        'living': '#D5A6BD',            # Mauve
        'dining': '#F4C7AB',            # Peach
        'garden': '#93C47D',            # Grass green
        'default': '#CCCCCC',           # Gray
    }

    # Text colors for readability
    TEXT_COLOR = '#2C3E50'
    DIMENSION_COLOR = '#34495E'
    BOUNDARY_COLOR = '#2C3E50'
    SETBACK_COLOR = '#E74C3C'
    GRID_COLOR = '#ECF0F1'

    def __init__(self, output_dir: str = "./output"):
        """
        Initialize visualization service.

        Args:
            output_dir: Directory to save generated images
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Visualization service initialized: output_dir={self.output_dir}")

    # Additional colors for architectural elements
    CORRIDOR_COLOR = '#F0F0F0'          # Light gray for corridors
    WALL_COLOR = '#000000'              # Black for walls
    DOOR_COLOR = '#8B4513'              # Brown for doors
    FIXTURE_COLORS = {
        'toilet': '#4A90E2',            # Blue
        'sink': '#50C878',              # Green
        'stove': '#E74C3C',             # Red
        'refrigerator': '#95A5A6',      # Gray
    }

    def generate_floor_plan(
        self,
        land_input: LandInputSchema,
        layout: LayoutOutputSchema,
        filename: Optional[str] = None,
        show_dimensions: bool = True,
        show_labels: bool = True,
        show_setbacks: bool = True,
        show_architectural: bool = True,
        dpi: int = 150,
    ) -> str:
        """
        Generate a floor plan image from layout data.

        Args:
            land_input: Original land input parameters
            layout: Optimized layout with rooms
            filename: Output filename (auto-generated if None)
            show_dimensions: Show room dimensions
            show_labels: Show room labels
            show_setbacks: Show setback lines
            show_architectural: Show walls, doors, corridors, fixtures
            dpi: Image resolution

        Returns:
            Path to generated image file
        """
        if filename is None:
            filename = f"floor_plan_{land_input.length}x{land_input.width}_{layout.fitness_score:.0f}.png"

        output_path = self.output_dir / filename

        logger.info(f"Generating floor plan: {filename}")

        # Create figure
        fig, ax = plt.subplots(figsize=(14, 10))

        # Get buildable area
        buildable = SriLankanBuildingRules.get_buildable_area(
            land_input.length,
            land_input.width,
            land_input.total_area
        )

        # Draw land boundary
        self._draw_land_boundary(ax, land_input)

        # Draw setback lines
        if show_setbacks:
            self._draw_setbacks(ax, buildable, land_input)

        # Draw architectural elements (walls, corridors, doors, fixtures)
        if show_architectural and hasattr(layout, 'architectural_elements'):
            elements = layout.architectural_elements

            # Draw corridors first (background)
            if 'corridors' in elements:
                self._draw_corridors(ax, elements['corridors'])

            # Draw rooms (labels and text)
            self._draw_rooms(ax, layout.rooms, show_labels, show_dimensions)

            # Draw walls (on top of rooms)
            if 'walls' in elements:
                self._draw_walls(ax, elements['walls'])

            # Draw WINDOWS for ventilation - CRITICAL!
            if 'windows' in elements:
                self._draw_windows(ax, elements['windows'])

            # Draw doors
            if 'doors' in elements:
                self._draw_doors(ax, elements['doors'])

            # Draw fixtures
            if 'fixtures' in elements:
                self._draw_fixtures(ax, elements['fixtures'])

            # Draw beds in bedrooms
            for room in layout.rooms:
                if 'bedroom' in room.type.lower():
                    self._draw_bed(ax, room)

        else:
            # Standard drawing without architectural elements
            self._draw_rooms(ax, layout.rooms, show_labels, show_dimensions)

        # Add professional title at bottom (like reference floor plans)
        self._add_professional_title(ax, land_input)

        # Add overall dimensions at top
        self._add_overall_dimensions(ax, land_input, buildable)

        # Set axes - CLEAN PROFESSIONAL STYLE
        ax.set_xlim(-1, land_input.width + 1)
        ax.set_ylim(-3, land_input.length + 2)  # Extra space for title
        ax.set_aspect('equal')

        # REMOVE axis labels and ticks for clean professional look
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_xticks([])
        ax.set_yticks([])

        # HIDE all spines for clean look
        for spine in ax.spines.values():
            spine.set_visible(False)

        plt.tight_layout()

        # Save
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()

        logger.info(f"Floor plan saved: {output_path}")
        return str(output_path)

    def generate_land_plot(
        self,
        land_input: LandInputSchema,
        filename: Optional[str] = None,
        dpi: int = 150,
    ) -> str:
        """
        Generate LAND PLOT visualization showing optimized buildable area.
        This is the FIRST output - showing the land with buildable area marked.

        Args:
            land_input: Original land input parameters
            filename: Output filename (auto-generated if None)
            dpi: Image resolution

        Returns:
            Path to generated image file
        """
        if filename is None:
            filename = f"land_plot_{land_input.length}x{land_input.width}.png"

        output_path = self.output_dir / filename

        logger.info(f"Generating land plot visualization: {filename}")

        # Create figure
        fig, ax = plt.subplots(figsize=(14, 10))

        # Get buildable area
        buildable = SriLankanBuildingRules.get_buildable_area(
            land_input.length,
            land_input.width,
            land_input.total_area
        )

        # Draw land boundary
        self._draw_land_boundary(ax, land_input)

        # Draw buildable area with HIGHLIGHTED fill
        buildable_rect = Rectangle(
            (buildable['offset_x'], buildable['offset_y']),
            buildable['width'],
            buildable['length'],
            fill=True,
            facecolor='#E8F5E9',  # Light green fill to show buildable area
            edgecolor='#4CAF50',   # Green border
            linewidth=3,
            linestyle='-',
            alpha=0.3,
            zorder=2
        )
        ax.add_patch(buildable_rect)

        # Add buildable area label with dimensions
        buildable_area_sqm = buildable['width'] * buildable['length']
        ax.text(
            buildable['offset_x'] + buildable['width'] / 2,
            buildable['offset_y'] + buildable['length'] / 2,
            f'BUILDABLE AREA\n{buildable["width"]:.1f}m × {buildable["length"]:.1f}m\n({buildable_area_sqm:.1f} m²)',
            ha='center',
            va='center',
            fontsize=14,
            fontweight='bold',
            color='#2E7D32',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='white', edgecolor='#4CAF50', linewidth=2),
            zorder=5
        )

        # Add setback annotations
        setback_front = buildable['offset_y']
        setback_rear = land_input.length - (buildable['offset_y'] + buildable['length'])
        setback_left = buildable['offset_x']
        setback_right = land_input.width - (buildable['offset_x'] + buildable['width'])

        # Front setback
        if setback_front > 0:
            ax.annotate(
                f'Front Setback\n{setback_front:.1f}m',
                xy=(land_input.width / 2, setback_front / 2),
                ha='center',
                va='center',
                fontsize=9,
                color='#D32F2F',
                style='italic'
            )

        # Rear setback
        if setback_rear > 0:
            ax.annotate(
                f'Rear Setback\n{setback_rear:.1f}m',
                xy=(land_input.width / 2, buildable['offset_y'] + buildable['length'] + setback_rear / 2),
                ha='center',
                va='center',
                fontsize=9,
                color='#D32F2F',
                style='italic'
            )

        # Left setback
        if setback_left > 0:
            ax.annotate(
                f'Left\nSetback\n{setback_left:.1f}m',
                xy=(setback_left / 2, land_input.length / 2),
                ha='center',
                va='center',
                fontsize=9,
                color='#D32F2F',
                style='italic'
            )

        # Right setback
        if setback_right > 0:
            ax.annotate(
                f'Right\nSetback\n{setback_right:.1f}m',
                xy=(buildable['offset_x'] + buildable['width'] + setback_right / 2, land_input.length / 2),
                ha='center',
                va='center',
                fontsize=9,
                color='#D32F2F',
                style='italic'
            )

        # Add title at top
        total_land_area = land_input.width * land_input.length
        ax.text(
            land_input.width / 2,
            land_input.length + 1.0,
            f'LAND PLOT - {land_input.width:.1f}m × {land_input.length:.1f}m ({total_land_area:.1f} m²)',
            ha='center',
            va='bottom',
            fontsize=16,
            fontweight='bold',
            color=self.BOUNDARY_COLOR
        )

        # Add professional title at bottom
        ax.text(
            land_input.width / 2,
            -2.0,
            'OPTIMIZED BUILDABLE AREA',
            ha='center',
            va='top',
            fontsize=20,
            fontweight='bold',
            color=self.TEXT_COLOR
        )

        # Set axes - CLEAN PROFESSIONAL STYLE
        ax.set_xlim(-1, land_input.width + 1)
        ax.set_ylim(-3, land_input.length + 2)
        ax.set_aspect('equal')

        # REMOVE axis labels and ticks for clean professional look
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_xticks([])
        ax.set_yticks([])

        # HIDE all spines for clean look
        for spine in ax.spines.values():
            spine.set_visible(False)

        plt.tight_layout()

        # Save
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()

        logger.info(f"Land plot saved: {output_path}")
        return str(output_path)

    def _draw_land_boundary(self, ax, land_input: LandInputSchema):
        """Draw the outer land boundary."""
        boundary = Rectangle(
            (0, 0),
            land_input.width,
            land_input.length,
            fill=False,
            edgecolor=self.BOUNDARY_COLOR,
            linewidth=3,
            linestyle='-',
            zorder=1
        )
        ax.add_patch(boundary)

        # Add land dimension labels
        # Width label (bottom)
        ax.annotate(
            f'{land_input.width:.1f}m',
            xy=(land_input.width / 2, -0.5),
            ha='center',
            va='top',
            fontsize=10,
            fontweight='bold',
            color=self.BOUNDARY_COLOR
        )

        # Length label (left)
        ax.annotate(
            f'{land_input.length:.1f}m',
            xy=(-0.5, land_input.length / 2),
            ha='right',
            va='center',
            fontsize=10,
            fontweight='bold',
            color=self.BOUNDARY_COLOR,
            rotation=90
        )

    def _draw_setbacks(self, ax, buildable: Dict[str, float], land_input: LandInputSchema):
        """Draw setback boundary lines."""
        setback_rect = Rectangle(
            (buildable['offset_x'], buildable['offset_y']),
            buildable['width'],
            buildable['length'],
            fill=False,
            edgecolor=self.SETBACK_COLOR,
            linewidth=2,
            linestyle='--',
            alpha=0.7,
            zorder=2
        )
        ax.add_patch(setback_rect)

        # Add setback labels
        ax.text(
            buildable['offset_x'] + buildable['width'] / 2,
            buildable['offset_y'] - 0.3,
            'Buildable Area',
            ha='center',
            va='top',
            fontsize=9,
            color=self.SETBACK_COLOR,
            style='italic'
        )

    def _meters_to_feet_inches(self, meters: float) -> str:
        """Convert meters to feet and inches format like professional floor plans."""
        total_inches = meters * 39.3701  # 1 meter = 39.3701 inches
        feet = int(total_inches // 12)
        inches = int(total_inches % 12)
        return f"{feet}'-{inches}\""

    def _draw_rooms(
        self,
        ax,
        rooms: List[RoomSchema],
        show_labels: bool,
        show_dimensions: bool
    ):
        """
        Draw rooms in PROFESSIONAL ARCHITECTURAL STYLE.
        NO colored backgrounds - just like real architectural floor plans!
        """
        for i, room in enumerate(rooms):
            # PROFESSIONAL STYLE: Do NOT draw colored backgrounds!
            # Real architectural floor plans don't have colored rooms.
            # Walls define the rooms, not colored rectangles.

            # Skip drawing room backgrounds entirely
            # (Walls will be drawn separately with proper thickness)

            # Room center
            center_x = room.center_x
            center_y = room.center_y

            # Add room label - PROFESSIONAL ARCHITECTURAL STYLE
            if show_labels:
                # Format room type (capitalize, replace underscores)
                room_type = room.type.replace('_', ' ').upper()

                # Convert dimensions to feet and inches
                width_ft = self._meters_to_feet_inches(room.width)
                height_ft = self._meters_to_feet_inches(room.height)

                # PROFESSIONAL: Room name in uppercase
                ax.text(
                    center_x,
                    center_y + 0.4,
                    room_type,
                    ha='center',
                    va='center',
                    fontsize=11,
                    fontweight='bold',
                    color='#000000',
                    zorder=100,
                    family='sans-serif'
                )

                # Dimensions in feet and inches - below room name
                dimensions_text = f'{width_ft} x {height_ft}'
                ax.text(
                    center_x,
                    center_y - 0.1,
                    dimensions_text,
                    ha='center',
                    va='center',
                    fontsize=9,
                    color='#000000',
                    zorder=100,
                    family='sans-serif'
                )

            # Add dimension annotations outside (optional, can be disabled)
            # The reference floor plans show dimensions INSIDE the rooms, so we skip external annotations

    def _draw_windows(self, ax, walls: List, buildable: Dict):
        """
        Draw window symbols in exterior walls (professional architectural style).
        Windows are shown as gaps or special marks in the walls.
        """
        # Add windows on exterior walls (typically on front and side walls)
        # Front wall (assuming north/top)
        front_wall_y = buildable['offset_y']
        wall_start_x = buildable['offset_x']
        wall_end_x = buildable['offset_x'] + buildable['width']

        # Add 2-3 windows on front wall
        num_windows = 3
        window_width = 1.2  # meters
        spacing = (wall_end_x - wall_start_x) / (num_windows + 1)

        for i in range(num_windows):
            window_x = wall_start_x + spacing * (i + 1) - window_width / 2
            # Draw window as two parallel lines
            ax.plot(
                [window_x, window_x + window_width],
                [front_wall_y, front_wall_y],
                color='#FFFFFF',
                linewidth=4,
                zorder=11,
                solid_capstyle='butt'
            )
            # Add window frame indicators
            ax.plot(
                [window_x, window_x + window_width],
                [front_wall_y, front_wall_y],
                color='#000000',
                linewidth=1,
                zorder=12,
                linestyle='-'
            )

    def _add_professional_title(self, ax, land_input: LandInputSchema):
        """Add professional 'FLOOR PLAN' title at bottom like reference images."""
        # Get the current axes limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        # Add "FLOOR PLAN" text at bottom center
        title_y = ylim[0] - 1.5  # Below the floor plan
        title_x = (xlim[0] + xlim[1]) / 2

        ax.text(
            title_x,
            title_y,
            'FLOOR PLAN',
            ha='center',
            va='top',
            fontsize=20,
            fontweight='bold',
            color='#000000',
            family='sans-serif',
            zorder=100
        )

        # Add horizontal line above title
        line_width = (xlim[1] - xlim[0]) * 0.4
        ax.plot(
            [title_x - line_width/2, title_x + line_width/2],
            [title_y + 0.3, title_y + 0.3],
            color='#000000',
            linewidth=2,
            zorder=100
        )

    def _add_overall_dimensions(self, ax, land_input: LandInputSchema, buildable: Dict):
        """Add overall floor plan dimensions at top (like reference images)."""
        # Convert to feet
        width_ft = self._meters_to_feet_inches(buildable['width'])
        height_ft = self._meters_to_feet_inches(buildable['length'])

        # Add dimension text at top center
        dim_text = f"{width_ft} × {height_ft}"

        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        ax.text(
            (xlim[0] + xlim[1]) / 2,
            ylim[1] + 1.0,
            dim_text,
            ha='center',
            va='bottom',
            fontsize=14,
            fontweight='bold',
            color='#000000',
            family='sans-serif',
            zorder=100
        )

    def _draw_grid(self, ax, land_input: LandInputSchema):
        """Draw background grid - DISABLED for professional look."""
        # Professional floor plans don't have grids - pure white background
        pass

    def _add_title_and_info(
        self,
        ax,
        land_input: LandInputSchema,
        layout: LayoutOutputSchema
    ):
        """Add title and layout information."""
        # Calculate total_area if not provided
        total_area = land_input.total_area or (land_input.length * land_input.width)

        # Title
        title = (
            f"Optimized House Layout - {land_input.length}m × {land_input.width}m "
            f"({total_area:.0f} m²)\n"
            f"Fitness Score: {layout.fitness_score:.1f}/100"
        )
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.TEXT_COLOR, pad=20)

        # Info box (top right)
        info_text = (
            f"Bedrooms: {land_input.bedrooms}\n"
            f"Toilets: {land_input.toilets}\n"
            f"Efficiency: {layout.efficiency_score:.1f}%\n"
            f"Sunlight: {layout.sunlight_score:.1f}%\n"
            f"Privacy: {layout.privacy_score:.1f}%\n"
            f"Compliance: {layout.regulation_compliance:.1f}%"
        )

        # Add text box
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.3)
        ax.text(
            0.98,
            0.98,
            info_text,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment='top',
            horizontalalignment='right',
            bbox=props,
            family='monospace'
        )

    def _add_legend(self, ax, rooms: List[RoomSchema]):
        """Add color legend for room types."""
        # Get unique room types in this layout
        room_types = list(set(room.type for room in rooms))
        room_types.sort()

        # Create legend elements
        legend_elements = []
        for room_type in room_types:
            color = self.ROOM_COLORS.get(room_type, self.ROOM_COLORS['default'])
            label = room_type.replace('_', ' ').title()
            legend_elements.append(
                patches.Patch(facecolor=color, edgecolor=self.TEXT_COLOR, label=label)
            )

        # Add legend
        ax.legend(
            handles=legend_elements,
            loc='upper left',
            fontsize=9,
            framealpha=0.9,
            title='Room Types',
            title_fontsize=10
        )

    def generate_comparison_image(
        self,
        land_input: LandInputSchema,
        layouts: List[LayoutOutputSchema],
        filename: Optional[str] = None,
        dpi: int = 120,
    ) -> str:
        """
        Generate comparison image showing multiple layouts side by side.

        Args:
            land_input: Land input parameters
            layouts: List of layouts to compare (max 4)
            filename: Output filename
            dpi: Image resolution

        Returns:
            Path to generated comparison image
        """
        if filename is None:
            filename = f"comparison_{land_input.length}x{land_input.width}.png"

        output_path = self.output_dir / filename

        num_layouts = min(len(layouts), 4)
        if num_layouts == 0:
            raise ValueError("No layouts provided for comparison")

        logger.info(f"Generating comparison image with {num_layouts} layouts")

        # Create subplots
        if num_layouts <= 2:
            fig, axes = plt.subplots(1, num_layouts, figsize=(12 * num_layouts, 10))
        else:
            fig, axes = plt.subplots(2, 2, figsize=(20, 16))

        if num_layouts == 1:
            axes = [axes]
        else:
            axes = axes.flatten()

        # Get buildable area
        buildable = SriLankanBuildingRules.get_buildable_area(
            land_input.length,
            land_input.width,
            land_input.total_area
        )

        # Draw each layout
        for idx, (ax, layout) in enumerate(zip(axes[:num_layouts], layouts)):
            # Draw components
            self._draw_land_boundary(ax, land_input)
            self._draw_setbacks(ax, buildable, land_input)
            self._draw_rooms(ax, layout.rooms, show_labels=True, show_dimensions=False)
            self._draw_grid(ax, land_input)

            # Subplot title
            ax.set_title(
                f"Layout {idx + 1} - Fitness: {layout.fitness_score:.1f}/100",
                fontsize=12,
                fontweight='bold',
                color=self.TEXT_COLOR
            )

            # Set axes
            ax.set_xlim(-1, land_input.width + 1)
            ax.set_ylim(-1, land_input.length + 1)
            ax.set_aspect('equal')
            ax.set_xlabel('Width (m)', fontsize=10)
            ax.set_ylabel('Length (m)', fontsize=10)

        # Hide unused subplots
        for idx in range(num_layouts, len(axes)):
            axes[idx].axis('off')

        # Overall title
        fig.suptitle(
            f'Layout Comparison - {land_input.length}m × {land_input.width}m',
            fontsize=16,
            fontweight='bold',
            color=self.TEXT_COLOR
        )

        plt.tight_layout()
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()

        logger.info(f"Comparison image saved: {output_path}")
        return str(output_path)

    def generate_score_chart(
        self,
        layout: LayoutOutputSchema,
        filename: Optional[str] = None,
        dpi: int = 120,
    ) -> str:
        """
        Generate radar chart showing all fitness scores.

        Args:
            layout: Layout with scores
            filename: Output filename
            dpi: Image resolution

        Returns:
            Path to generated chart image
        """
        if filename is None:
            filename = f"scores_{layout.fitness_score:.0f}.png"

        output_path = self.output_dir / filename

        logger.info("Generating score radar chart")

        # Prepare data
        categories = ['Space\nEfficiency', 'Sunlight', 'Privacy', 'Circulation', 'Regulation\nCompliance']
        values = [
            layout.efficiency_score,
            layout.sunlight_score,
            layout.privacy_score,
            getattr(layout, 'circulation_score', 75),  # Default if not available
            layout.regulation_compliance,
        ]

        # Number of variables
        N = len(categories)

        # Compute angle for each axis
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        values += values[:1]  # Complete the circle
        angles += angles[:1]

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

        # Draw the plot
        ax.plot(angles, values, 'o-', linewidth=2, color='#3498DB')
        ax.fill(angles, values, alpha=0.25, color='#3498DB')

        # Fix axis to go in the right order
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)

        # Draw axis lines for each angle and label
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11)

        # Set y-axis limits
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9, alpha=0.7)

        # Add title
        plt.title(
            f'Layout Performance Scores\nOverall Fitness: {layout.fitness_score:.1f}/100',
            fontsize=14,
            fontweight='bold',
            color=self.TEXT_COLOR,
            pad=20
        )

        plt.tight_layout()
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()

        logger.info(f"Score chart saved: {output_path}")
        return str(output_path)

    def generate_evolution_plot(
        self,
        fitness_history: List[float],
        filename: Optional[str] = None,
        dpi: int = 120,
    ) -> str:
        """
        Generate plot showing fitness evolution over generations.

        Args:
            fitness_history: List of best fitness per generation
            filename: Output filename
            dpi: Image resolution

        Returns:
            Path to generated plot
        """
        if filename is None:
            filename = "evolution.png"

        output_path = self.output_dir / filename

        logger.info("Generating evolution plot")

        fig, ax = plt.subplots(figsize=(12, 6))

        generations = range(1, len(fitness_history) + 1)

        ax.plot(
            generations,
            fitness_history,
            marker='o',
            linestyle='-',
            linewidth=2,
            markersize=5,
            color='#2ECC71'
        )

        ax.set_xlabel('Generation', fontsize=12, fontweight='bold')
        ax.set_ylabel('Best Fitness Score', fontsize=12, fontweight='bold')
        ax.set_title(
            f'Genetic Algorithm Evolution\nFinal Fitness: {fitness_history[-1]:.2f}',
            fontsize=14,
            fontweight='bold'
        )

        ax.grid(True, alpha=0.3)
        ax.set_xlim(1, len(fitness_history))
        ax.set_ylim(0, 100)

        plt.tight_layout()
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()

        logger.info(f"Evolution plot saved: {output_path}")
        return str(output_path)

    def _draw_corridors(self, ax, corridors: List):
        """
        Draw corridors/hallways.

        Args:
            ax: Matplotlib axes
            corridors: List of Corridor objects
        """
        for corridor in corridors:
            corridor_patch = Rectangle(
                (corridor.x, corridor.y),
                corridor.width,
                corridor.height,
                facecolor=self.CORRIDOR_COLOR,
                edgecolor='#AAAAAA',
                linewidth=1.5,
                linestyle='--',
                alpha=0.6,
                zorder=2
            )
            ax.add_patch(corridor_patch)

            # Add corridor label
            center_x = corridor.x + corridor.width / 2
            center_y = corridor.y + corridor.height / 2
            ax.text(
                center_x, center_y,
                'CORRIDOR',
                ha='center', va='center',
                fontsize=9,
                fontweight='bold',
                color='#555555',
                alpha=0.7,
                zorder=2.5
            )

    def _draw_walls(self, ax, walls: List):
        """
        Draw walls with THICK BLACK appearance like professional floor plans.
        Walls are SOLID BLACK rectangles!

        Args:
            ax: Matplotlib axes
            walls: List of Wall objects
        """
        for wall in walls:
            # PROFESSIONAL wall thickness - THICK like reference images
            wall_thickness = 0.25 if wall.is_exterior else 0.15  # Thicker walls

            # Calculate perpendicular offset for wall thickness
            dx = wall.x2 - wall.x1
            dy = wall.y2 - wall.y1
            length = np.sqrt(dx**2 + dy**2)

            if length > 0:
                # Perpendicular unit vector
                perp_x = -dy / length * wall_thickness / 2
                perp_y = dx / length * wall_thickness / 2

                # Create wall polygon (rectangle with thickness)
                wall_poly = patches.Polygon([
                    (wall.x1 + perp_x, wall.y1 + perp_y),
                    (wall.x2 + perp_x, wall.y2 + perp_y),
                    (wall.x2 - perp_x, wall.y2 - perp_y),
                    (wall.x1 - perp_x, wall.y1 - perp_y),
                ],
                closed=True,
                facecolor='#000000',  # SOLID BLACK for all walls (professional look)
                edgecolor='#000000',
                linewidth=0,  # No edge line needed
                zorder=10
                )
                ax.add_patch(wall_poly)

    def _draw_doors(self, ax, doors: List):
        """
        Draw doors with professional swing arcs (like reference floor plans).

        Args:
            ax: Matplotlib axes
            doors: List of Door objects
        """
        for door in doors:
            # PROFESSIONAL STYLE: Door with visible swing arc
            door_color = '#000000'  # Black for professional look

            if door.orientation == 'horizontal':
                # Horizontal door - draw door leaf (line)
                ax.plot(
                    [door.x, door.x + door.width],
                    [door.y, door.y],
                    color=door_color,
                    linewidth=2.5,
                    zorder=11,
                    solid_capstyle='round'
                )

                # Draw prominent swing arc
                arc = patches.Arc(
                    (door.x if door.swing_direction == 'up' else door.x + door.width, door.y),
                    door.width * 2, door.width * 2,
                    angle=0,
                    theta1=0, theta2=90,
                    color=door_color,
                    linewidth=1.5,
                    linestyle='-',
                    zorder=11
                )
                ax.add_patch(arc)

            else:  # vertical door
                # Vertical door - draw door leaf (line)
                ax.plot(
                    [door.x, door.x],
                    [door.y, door.y + door.width],
                    color=door_color,
                    linewidth=2.5,
                    zorder=11,
                    solid_capstyle='round'
                )

                # Draw prominent swing arc
                arc = patches.Arc(
                    (door.x, door.y if door.swing_direction == 'right' else door.y + door.width),
                    door.width * 2, door.width * 2,
                    angle=0,
                    theta1=0, theta2=90,
                    color=door_color,
                    linewidth=1.5,
                    linestyle='-',
                    zorder=11
                )
                ax.add_patch(arc)

    def _draw_windows(self, ax, windows: List):
        """
        Draw WINDOWS for ventilation - ESSENTIAL for realistic floor plans!
        Windows shown as breaks in exterior walls with parallel lines.

        Args:
            ax: Matplotlib axes
            windows: List of Window objects
        """
        for window in windows:
            window_color = '#0066CC'  # Blue to indicate glass/opening

            if window.orientation == 'horizontal':
                # Horizontal window (on top/bottom wall)
                # Draw window opening as thick line
                ax.plot(
                    [window.x, window.x + window.width],
                    [window.y, window.y],
                    color=window_color,
                    linewidth=4,
                    zorder=11,
                    solid_capstyle='butt'
                )

                # Draw glass indicator (parallel line)
                ax.plot(
                    [window.x + 0.1, window.x + window.width - 0.1],
                    [window.y, window.y],
                    color=window_color,
                    linewidth=1,
                    zorder=11,
                    alpha=0.6
                )

            else:  # vertical window (on left/right wall)
                # Vertical window
                # Draw window opening as thick line
                ax.plot(
                    [window.x, window.x],
                    [window.y, window.y + window.width],
                    color=window_color,
                    linewidth=4,
                    zorder=11,
                    solid_capstyle='butt'
                )

                # Draw glass indicator (parallel line)
                ax.plot(
                    [window.x, window.x],
                    [window.y + 0.1, window.y + window.width - 0.1],
                    color=window_color,
                    linewidth=1,
                    zorder=11,
                    alpha=0.6
                )

    def _draw_bed(self, ax, room: RoomSchema):
        """Draw a bed symbol in a bedroom (professional architectural style)."""
        # Place bed in center of room
        bed_width = min(room.width * 0.4, 2.0)  # Max 2m wide
        bed_height = min(room.height * 0.5, 2.5)  # Max 2.5m long

        bed_x = room.center_x - bed_width / 2
        bed_y = room.center_y - bed_height / 2

        # Draw bed frame (rectangle)
        bed_frame = Rectangle(
            (bed_x, bed_y),
            bed_width,
            bed_height,
            facecolor='white',
            edgecolor='#000000',
            linewidth=2,
            zorder=12
        )
        ax.add_patch(bed_frame)

        # Draw pillow area (top of bed)
        pillow_height = bed_height * 0.25
        pillow = Rectangle(
            (bed_x, bed_y + bed_height - pillow_height),
            bed_width,
            pillow_height,
            facecolor='#E0E0E0',
            edgecolor='#000000',
            linewidth=1,
            zorder=13
        )
        ax.add_patch(pillow)

    def _draw_fixtures(self, ax, fixtures: List):
        """
        Draw fixtures as PROFESSIONAL ARCHITECTURAL SYMBOLS.
        Like real architectural floor plans!

        Args:
            ax: Matplotlib axes
            fixtures: List of Fixture objects
        """
        for fixture in fixtures:
            center_x = fixture.x + fixture.width / 2
            center_y = fixture.y + fixture.height / 2

            if fixture.type == 'toilet':
                # Toilet: oval (bowl) + small rectangle (tank)
                bowl = patches.Ellipse(
                    (center_x, center_y - 0.1),
                    fixture.width * 0.6,
                    fixture.height * 0.7,
                    facecolor='white',
                    edgecolor='#000000',
                    linewidth=2,
                    zorder=12
                )
                ax.add_patch(bowl)

                # Tank
                tank = Rectangle(
                    (center_x - fixture.width * 0.2, center_y + fixture.height * 0.2),
                    fixture.width * 0.4,
                    fixture.height * 0.3,
                    facecolor='white',
                    edgecolor='#000000',
                    linewidth=2,
                    zorder=12
                )
                ax.add_patch(tank)

            elif fixture.type == 'sink':
                # Sink: oval shape with faucet indicator
                sink_oval = patches.Ellipse(
                    (center_x, center_y),
                    fixture.width * 0.7,
                    fixture.height * 0.5,
                    facecolor='white',
                    edgecolor='#000000',
                    linewidth=2,
                    zorder=12
                )
                ax.add_patch(sink_oval)

                # Faucet (small circle at top)
                faucet = patches.Circle(
                    (center_x, center_y + fixture.height * 0.3),
                    0.08,
                    facecolor='#000000',
                    zorder=13
                )
                ax.add_patch(faucet)

            elif fixture.type == 'stove':
                # Stove: rectangle with 4 burners
                stove_rect = Rectangle(
                    (fixture.x, fixture.y),
                    fixture.width,
                    fixture.height,
                    facecolor='white',
                    edgecolor='#000000',
                    linewidth=2,
                    zorder=12
                )
                ax.add_patch(stove_rect)

                # 4 burners (circles)
                burner_radius = 0.1
                for i in range(2):
                    for j in range(2):
                        burner_x = fixture.x + (i + 0.5) * fixture.width / 2
                        burner_y = fixture.y + (j + 0.5) * fixture.height / 2
                        burner = patches.Circle(
                            (burner_x, burner_y),
                            burner_radius,
                            facecolor='none',
                            edgecolor='#000000',
                            linewidth=1.5,
                            zorder=13
                        )
                        ax.add_patch(burner)

            elif fixture.type == 'refrigerator':
                # Refrigerator: rectangle with dividing line
                fridge = Rectangle(
                    (fixture.x, fixture.y),
                    fixture.width,
                    fixture.height,
                    facecolor='white',
                    edgecolor='#000000',
                    linewidth=2,
                    zorder=12
                )
                ax.add_patch(fridge)

                # Dividing line (freezer/fridge)
                ax.plot(
                    [fixture.x, fixture.x + fixture.width],
                    [center_y, center_y],
                    color='#000000',
                    linewidth=1.5,
                    zorder=13
                )

            elif fixture.type == 'bed':
                # Bed is now drawn separately via _draw_bed method
                pass
