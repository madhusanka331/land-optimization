"""
Integration tests for end-to-end optimization workflows.
Tests complete user journeys through the system.
"""

import pytest
from pathlib import Path


@pytest.mark.integration
class TestCompleteOptimizationFlow:
    """Test complete optimization workflow from input to visualization."""

    @pytest.mark.slow
    def test_full_optimization_workflow(self, client, sample_land_input):
        """Test complete workflow: validate -> optimize -> retrieve."""

        # Step 1: Validate input
        validation_response = client.post(
            "/api/v1/optimization/validate",
            json=sample_land_input.model_dump()
        )

        assert validation_response.status_code == 200
        validation_data = validation_response.json()
        assert validation_data["valid"] is True

        # Step 2: Run optimization
        optimization_request = {
            "land_input": sample_land_input.model_dump(),
            "generations": 10,  # Low for faster testing
            "population_size": 20,
        }

        optimization_response = client.post(
            "/api/v1/optimization/optimize",
            json=optimization_request
        )

        assert optimization_response.status_code == 200
        optimization_data = optimization_response.json()
        assert optimization_data["success"] is True
        assert "layout" in optimization_data
        assert "optimization_id" in optimization_data

        optimization_id = optimization_data["optimization_id"]

        # Step 3: Retrieve from history
        history_response = client.get(
            f"/api/v1/optimization/history/{optimization_id}"
        )

        assert history_response.status_code == 200
        history_data = history_response.json()
        assert history_data["id"] == optimization_id
        assert "layout_data" in history_data
        assert "scores" in history_data

        # Step 4: Verify in history list
        list_response = client.get("/api/v1/optimization/history")

        assert list_response.status_code == 200
        list_data = list_response.json()
        assert len(list_data) >= 1
        assert any(opt["id"] == optimization_id for opt in list_data)

    @pytest.mark.slow
    def test_multiple_optimizations_same_input(self, client, sample_land_input):
        """Test running multiple optimizations on same input."""

        request_data = {
            "land_input": sample_land_input.model_dump(),
            "generations": 5,
            "population_size": 10,
        }

        # Run first optimization
        response1 = client.post(
            "/api/v1/optimization/optimize",
            json=request_data
        )

        assert response1.status_code == 200
        data1 = response1.json()

        # Run second optimization
        response2 = client.post(
            "/api/v1/optimization/optimize",
            json=request_data
        )

        assert response2.status_code == 200
        data2 = response2.json()

        # Both should succeed
        assert data1["success"] is True
        assert data2["success"] is True

        # IDs should be different
        assert data1["optimization_id"] != data2["optimization_id"]

    @pytest.mark.slow
    def test_optimization_with_different_inputs(
        self,
        client,
        small_land_input,
        large_land_input
    ):
        """Test optimizations with different land sizes."""

        # Optimize small land
        small_request = {
            "land_input": small_land_input.model_dump(),
            "generations": 5,
            "population_size": 10,
        }

        small_response = client.post(
            "/api/v1/optimization/optimize",
            json=small_request
        )

        assert small_response.status_code == 200
        small_data = small_response.json()

        # Optimize large land
        large_request = {
            "land_input": large_land_input.model_dump(),
            "generations": 5,
            "population_size": 10,
        }

        large_response = client.post(
            "/api/v1/optimization/optimize",
            json=large_request
        )

        assert large_response.status_code == 200
        large_data = large_response.json()

        # Both should succeed
        assert small_data["success"] is True
        assert large_data["success"] is True

        # Check room counts match requirements
        small_rooms = small_data["layout"]["rooms"]
        large_rooms = large_data["layout"]["rooms"]

        assert len(large_rooms) > len(small_rooms)


@pytest.mark.integration
class TestSearchAndFilter:
    """Test search and filter workflows."""

    @pytest.mark.slow
    def test_search_workflow(self, client, sample_land_input):
        """Test creating optimization and searching for it."""

        # Create optimization
        request_data = {
            "land_input": sample_land_input.model_dump(),
            "generations": 5,
            "population_size": 10,
        }

        create_response = client.post(
            "/api/v1/optimization/optimize",
            json=request_data
        )

        assert create_response.status_code == 200

        # Search by bedroom count
        search_response = client.get(
            f"/api/v1/optimization/search?bedrooms={sample_land_input.bedrooms}"
        )

        assert search_response.status_code == 200
        search_data = search_response.json()

        # Should find the optimization
        assert len(search_data) >= 1

    @pytest.mark.slow
    def test_best_optimizations_workflow(self, client, sample_land_input):
        """Test creating optimization and retrieving best results."""

        # Create optimization
        request_data = {
            "land_input": sample_land_input.model_dump(),
            "generations": 5,
            "population_size": 10,
        }

        client.post("/api/v1/optimization/optimize", json=request_data)

        # Get best optimizations
        best_response = client.get("/api/v1/optimization/best?min_fitness=0")

        assert best_response.status_code == 200
        best_data = best_response.json()

        assert len(best_data) >= 1


@pytest.mark.integration
class TestDeleteWorkflow:
    """Test delete workflow."""

    @pytest.mark.slow
    def test_create_and_delete_workflow(self, client, small_land_input):
        """Test creating and deleting optimization."""

        # Create optimization
        request_data = {
            "land_input": small_land_input.model_dump(),
            "generations": 5,
            "population_size": 10,
        }

        create_response = client.post(
            "/api/v1/optimization/optimize",
            json=request_data
        )

        assert create_response.status_code == 200
        optimization_id = create_response.json()["optimization_id"]

        # Verify it exists
        get_response = client.get(
            f"/api/v1/optimization/history/{optimization_id}"
        )
        assert get_response.status_code == 200

        # Delete it
        delete_response = client.delete(
            f"/api/v1/optimization/history/{optimization_id}"
        )
        assert delete_response.status_code == 200

        # Verify it's gone
        get_after_delete = client.get(
            f"/api/v1/optimization/history/{optimization_id}"
        )
        assert get_after_delete.status_code == 404


@pytest.mark.integration
class TestErrorRecovery:
    """Test error handling and recovery."""

    def test_invalid_input_recovery(self, client):
        """Test system recovers from invalid input."""

        # Send invalid request
        invalid_request = {
            "land_input": {
                "length": -10,
                "width": 15,
                "bedrooms": 3,
                "toilets": 2,
                "front_direction": "NORTH",
                "road_side": "SOUTH",
            }
        }

        response1 = client.post(
            "/api/v1/optimization/optimize",
            json=invalid_request
        )

        # Should fail
        assert response1.status_code in [400, 422]

        # System should still work after error
        health_response = client.get("/health")
        assert health_response.status_code == 200

    @pytest.mark.slow
    def test_optimization_failure_recovery(self, client):
        """Test system recovers from optimization failure."""

        # Try to optimize impossible requirements
        impossible_request = {
            "land_input": {
                "length": 5,
                "width": 3,
                "bedrooms": 20,  # Impossible for 15 sqm
                "toilets": 10,
                "front_direction": "NORTH",
                "road_side": "SOUTH",
            },
            "generations": 5,
            "population_size": 10,
        }

        response1 = client.post(
            "/api/v1/optimization/optimize",
            json=impossible_request
        )

        # Should fail validation
        assert response1.status_code == 400

        # System should still work
        health_response = client.get("/health")
        assert health_response.status_code == 200


@pytest.mark.integration
class TestVariousInputScenarios:
    """Test optimization with various input scenarios."""

    @pytest.mark.slow
    def test_minimal_house(self, client):
        """Test optimization for minimal house (1 bed, 1 bath)."""

        minimal_input = {
            "length": 12.0,
            "width": 10.0,
            "bedrooms": 1,
            "toilets": 1,
            "living_rooms": 0,
            "dining_rooms": 0,
            "kitchen": True,
            "garden_area": 0,
            "front_direction": "NORTH",
            "road_side": "SOUTH",
        }

        request_data = {
            "land_input": minimal_input,
            "generations": 5,
            "population_size": 10,
        }

        response = client.post(
            "/api/v1/optimization/optimize",
            json=request_data
        )

        assert response.status_code in [200, 400]  # May fail if land too small

    @pytest.mark.slow
    def test_house_with_garden(self, client, sample_land_input):
        """Test optimization with garden requirement."""

        sample_land_input.garden_area = 30.0

        request_data = {
            "land_input": sample_land_input.model_dump(),
            "generations": 5,
            "population_size": 10,
        }

        response = client.post(
            "/api/v1/optimization/optimize",
            json=request_data
        )

        if response.status_code == 200:
            data = response.json()
            rooms = data["layout"]["rooms"]

            # Should include garden
            garden_rooms = [r for r in rooms if r["type"] == "garden"]
            assert len(garden_rooms) >= 1

    @pytest.mark.slow
    def test_different_orientations(self, client, sample_land_input):
        """Test optimization with different land orientations."""

        from src.models.schemas import DirectionEnum

        orientations = [
            DirectionEnum.NORTH,
            DirectionEnum.SOUTH,
            DirectionEnum.EAST,
            DirectionEnum.WEST,
        ]

        for orientation in orientations:
            sample_land_input.front_direction = orientation

            request_data = {
                "land_input": sample_land_input.model_dump(),
                "generations": 5,
                "population_size": 10,
            }

            response = client.post(
                "/api/v1/optimization/optimize",
                json=request_data
            )

            assert response.status_code == 200


@pytest.mark.integration
class TestPerformance:
    """Test system performance characteristics."""

    @pytest.mark.slow
    def test_optimization_completes_in_reasonable_time(
        self,
        client,
        small_land_input
    ):
        """Test optimization completes within reasonable time."""

        import time

        request_data = {
            "land_input": small_land_input.model_dump(),
            "generations": 20,
            "population_size": 30,
        }

        start_time = time.time()

        response = client.post(
            "/api/v1/optimization/optimize",
            json=request_data,
            timeout=60  # 60 second timeout
        )

        elapsed_time = time.time() - start_time

        assert response.status_code == 200
        assert elapsed_time < 60  # Should complete within 60 seconds

    def test_api_response_time(self, client):
        """Test API endpoints respond quickly."""

        import time

        start_time = time.time()
        response = client.get("/")
        elapsed_time = time.time() - start_time

        assert response.status_code == 200
        assert elapsed_time < 1.0  # Should respond within 1 second
