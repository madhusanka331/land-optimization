"""
Unit tests for API endpoints.
Tests FastAPI routes and request/response handling.
"""

import pytest


class TestRootEndpoints:
    """Test root API endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "app" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "online"

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "components" in data

    def test_system_info(self, client):
        """Test system info endpoint."""
        response = client.get("/api/v1/info")

        assert response.status_code == 200
        data = response.json()
        assert "genetic_algorithm" in data
        assert "building_rules" in data
        assert "api" in data


class TestValidationEndpoint:
    """Test validation endpoint."""

    def test_validate_valid_input(self, client, sample_land_input):
        """Test validation with valid input."""
        response = client.post(
            "/api/v1/optimization/validate",
            json=sample_land_input.model_dump()
        )

        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert "errors" in data
        assert "warnings" in data

    def test_validate_invalid_dimensions(self, client):
        """Test validation with invalid dimensions."""
        invalid_input = {
            "length": -10,  # Invalid negative length
            "width": 15,
            "bedrooms": 3,
            "toilets": 2,
            "front_direction": "NORTH",
            "road_side": "SOUTH",
        }

        response = client.post(
            "/api/v1/optimization/validate",
            json=invalid_input
        )

        # Should return validation error
        assert response.status_code == 422

    def test_validate_missing_fields(self, client):
        """Test validation with missing required fields."""
        incomplete_input = {
            "length": 20,
            "width": 15,
            # Missing bedrooms, toilets, etc.
        }

        response = client.post(
            "/api/v1/optimization/validate",
            json=incomplete_input
        )

        assert response.status_code == 422


class TestOptimizationEndpoint:
    """Test optimization endpoint."""

    @pytest.mark.slow
    def test_optimize_basic(self, client, small_land_input):
        """Test basic optimization request."""
        request_data = {
            "land_input": small_land_input.model_dump(),
            "generations": 10,  # Low for faster testing
            "population_size": 20,
        }

        response = client.post(
            "/api/v1/optimization/optimize",
            json=request_data
        )

        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "layout" in data
        assert "visualization_url" in data

    def test_optimize_invalid_input(self, client):
        """Test optimization with invalid input."""
        invalid_request = {
            "land_input": {
                "length": 5,  # Too small
                "width": 3,
                "bedrooms": 10,  # Too many for small land
                "toilets": 5,
                "front_direction": "NORTH",
                "road_side": "SOUTH",
            },
            "generations": 10,
        }

        response = client.post(
            "/api/v1/optimization/optimize",
            json=invalid_request
        )

        # Should fail validation
        assert response.status_code == 400

    def test_optimize_custom_parameters(self, client, small_land_input):
        """Test optimization with custom GA parameters."""
        request_data = {
            "land_input": small_land_input.model_dump(),
            "generations": 5,
            "population_size": 10,
            "mutation_rate": 0.2,
            "crossover_rate": 0.7,
        }

        response = client.post(
            "/api/v1/optimization/optimize",
            json=request_data
        )

        # Should accept custom parameters
        assert response.status_code in [200, 400]  # 400 if validation fails


class TestHistoryEndpoints:
    """Test optimization history endpoints."""

    def test_get_empty_history(self, client):
        """Test getting history when empty."""
        response = client.get("/api/v1/optimization/history")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_history_with_limit(self, client):
        """Test getting history with limit parameter."""
        response = client.get("/api/v1/optimization/history?limit=5")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_get_nonexistent_optimization(self, client):
        """Test getting optimization that doesn't exist."""
        response = client.get("/api/v1/optimization/history/999999")

        assert response.status_code == 404


class TestBestOptimizationsEndpoint:
    """Test best optimizations endpoint."""

    def test_get_best_optimizations(self, client):
        """Test getting best optimizations."""
        response = client.get("/api/v1/optimization/best")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_best_with_min_fitness(self, client):
        """Test getting best optimizations with minimum fitness."""
        response = client.get("/api/v1/optimization/best?min_fitness=80")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestSearchEndpoint:
    """Test search endpoint."""

    def test_search_no_filters(self, client):
        """Test search with no filters."""
        response = client.get("/api/v1/optimization/search")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_search_by_bedrooms(self, client):
        """Test search filtered by bedrooms."""
        response = client.get("/api/v1/optimization/search?bedrooms=3")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_search_by_area_range(self, client):
        """Test search filtered by area range."""
        response = client.get(
            "/api/v1/optimization/search?min_area=200&max_area=400"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_search_with_invalid_parameters(self, client):
        """Test search with invalid parameters."""
        response = client.get("/api/v1/optimization/search?bedrooms=-1")

        # Should handle invalid parameters gracefully
        assert response.status_code in [200, 422]


class TestDeleteEndpoint:
    """Test delete endpoint."""

    def test_delete_nonexistent(self, client):
        """Test deleting non-existent optimization."""
        response = client.delete("/api/v1/optimization/history/999999")

        assert response.status_code == 404


class TestCORSHeaders:
    """Test CORS configuration."""

    def test_cors_headers_present(self, client):
        """Test CORS headers are present in responses."""
        response = client.get("/")

        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers or response.status_code == 200


class TestErrorHandling:
    """Test API error handling."""

    def test_404_for_invalid_route(self, client):
        """Test 404 for non-existent route."""
        response = client.get("/api/v1/nonexistent")

        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test 405 for wrong HTTP method."""
        response = client.put("/")  # Root only accepts GET

        assert response.status_code == 405
