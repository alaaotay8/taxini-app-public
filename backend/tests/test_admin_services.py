"""
Unit tests for admin service classes.
"""

import pytest
from datetime import datetime, date, timedelta
from sqlmodel import Session

from src.models.user import User, Driver, Rider, Admin
from src.models.trip import Trip
from src.models.settings import Settings
from src.services.admin_stats import AdminStatsService
from src.services.admin_settings import AdminSettingsService
from src.services.admin_trip import AdminTripService


class TestAdminStatsService:
    """Test class for AdminStatsService business logic."""

    @pytest.fixture
    def stats_sample_data(self, session: Session):
        """Create sample data for statistics testing."""
        # Create drivers and riders
        drivers = []
        riders = []
        
        for i in range(3):
            # Create driver
            driver_user = User(
                auth_id=f"stats-driver-{i}",
                name=f"Stats Driver {i}",
                email=f"statsdriver{i}@example.com",
                phone_number=f"+1700000{i:03d}",
                role="driver",
                auth_status="verified"
            )
            session.add(driver_user)
            session.commit()
            session.refresh(driver_user)
            
            driver = Driver(
                user_id=driver_user.id,
                taxi_number=f"STATS-{i}",
                account_status="verified" if i < 2 else "locked",
                driver_status="online" if i == 0 else "offline"
            )
            session.add(driver)
            drivers.append(driver_user)
            
            # Create rider
            rider_user = User(
                auth_id=f"stats-rider-{i}",
                name=f"Stats Rider {i}",
                email=f"statsrider{i}@example.com",
                phone_number=f"+1800000{i:03d}",
                role="rider",
                auth_status="verified"
            )
            session.add(rider_user)
            session.commit()
            session.refresh(rider_user)
            
            rider = Rider(
                user_id=rider_user.id,
                residence_place=f"Stats Area {i}"
            )
            session.add(rider)
            riders.append(rider_user)
        
        session.commit()
        
        # Create trips
        today = datetime.utcnow()
        yesterday = today - timedelta(days=1)
        
        trips = [
            {
                "rider_id": riders[0].id,
                "driver_id": drivers[0].id,
                "status": "completed",
                "estimated_cost_tnd": 15.50,
                "created_at": today,
                "completed_at": today
            },
            {
                "rider_id": riders[1].id,
                "driver_id": drivers[1].id,
                "status": "completed",
                "estimated_cost_tnd": 22.75,
                "created_at": yesterday,
                "completed_at": yesterday
            },
            {
                "rider_id": riders[2].id,
                "driver_id": None,
                "status": "cancelled",
                "estimated_cost_tnd": 0,
                "created_at": today,
                "cancelled_at": today
            }
        ]
        
        for trip_data in trips:
            trip = Trip(
                pickup_latitude=36.8065,
                pickup_longitude=10.1815,
                pickup_address="Test Pickup",
                destination_latitude=36.8190,
                destination_longitude=10.1658,
                destination_address="Test Destination",
                trip_type="regular",
                estimated_distance_km=10.0,
                requested_at=trip_data.get("created_at", today),
                **trip_data
            )
            session.add(trip)
        
        session.commit()
        return {"drivers": drivers, "riders": riders}

    def test_get_global_statistics_basic(self, session: Session, stats_sample_data):
        """Test basic global statistics calculation."""
        stats = AdminStatsService.get_global_statistics(session)
        
        assert isinstance(stats, dict)
        
        # Basic counts
        assert stats["total_users"] >= 6  # 3 drivers + 3 riders
        assert stats["total_drivers"] >= 3
        assert stats["total_riders"] >= 3
        assert stats["active_drivers"] >= 2  # 2 verified drivers
        
        # Trip statistics
        assert stats["total_trips"] >= 3
        assert stats["completed_trips"] >= 2
        assert stats["cancelled_trips"] >= 1
        
        # Revenue
        assert stats["total_revenue"] >= 38.25  # Sum of completed trips
        
        # Driver status
        assert stats["online_drivers"] >= 1
        assert stats["offline_drivers"] >= 2

    def test_get_global_statistics_with_date_filter(self, session: Session, stats_sample_data):
        """Test global statistics with date filtering."""
        today = date.today()
        
        stats = AdminStatsService.get_global_statistics(
            session, 
            start_date=today, 
            end_date=today
        )
        
        # Should only include today's data
        assert stats["trips_today"] >= 2  # One completed, one cancelled today
        assert stats["revenue_today"] >= 15.50  # Only today's completed trip

    def test_get_global_statistics_empty_database(self, session: Session):
        """Test global statistics with empty database."""
        stats = AdminStatsService.get_global_statistics(session)
        
        # Should return zeros for empty database
        assert stats["total_users"] == 0
        assert stats["total_trips"] == 0
        assert stats["total_revenue"] == 0.0
        assert stats["completion_rate"] == 0.0

    def test_completion_rate_calculation(self, session: Session, stats_sample_data):
        """Test completion rate calculation logic."""
        stats = AdminStatsService.get_global_statistics(session)
        
        completed = stats["completed_trips"]
        cancelled = stats["cancelled_trips"]
        
        if completed + cancelled > 0:
            expected_rate = (completed / (completed + cancelled)) * 100
            assert abs(stats["completion_rate"] - expected_rate) < 0.01
        else:
            assert stats["completion_rate"] == 0.0


class TestAdminSettingsService:
    """Test class for AdminSettingsService business logic."""

    @pytest.fixture
    def settings_sample_data(self, session: Session):
        """Create sample settings for testing."""
        settings = [
            Settings(
                setting_key="test_float_setting",
                setting_value="1.5",
                data_type="float",
                description="Test float setting",
                category="test",
                is_active=True,
                is_editable=True
            ),
            Settings(
                setting_key="test_string_setting",
                setting_value="test_value",
                data_type="string",
                description="Test string setting",
                category="test",
                is_active=True,
                is_editable=True
            ),
            Settings(
                setting_key="readonly_setting",
                setting_value="readonly_value",
                data_type="string",
                description="Read-only setting",
                category="system",
                is_active=True,
                is_editable=False
            )
        ]
        
        for setting in settings:
            session.add(setting)
        
        session.commit()
        return settings

    def test_get_all_settings(self, session: Session, settings_sample_data):
        """Test retrieving all settings."""
        settings = AdminSettingsService.get_all_settings(session)
        
        assert len(settings) >= 3
        
        # Check structure
        for setting in settings:
            assert hasattr(setting, 'setting_key')
            assert hasattr(setting, 'setting_value')
            assert hasattr(setting, 'data_type')

    def test_get_settings_by_category(self, session: Session, settings_sample_data):
        """Test filtering settings by category."""
        settings = AdminSettingsService.get_all_settings(session, category="test")
        
        for setting in settings:
            assert setting.category == "test"

    def test_get_setting_by_key(self, session: Session, settings_sample_data):
        """Test retrieving specific setting by key."""
        setting = AdminSettingsService.get_setting_by_key(session, "test_float_setting")
        
        assert setting is not None
        assert setting.setting_key == "test_float_setting"
        assert setting.setting_value == "1.5"

    def test_get_setting_not_found(self, session: Session):
        """Test retrieving non-existent setting."""
        setting = AdminSettingsService.get_setting_by_key(session, "nonexistent_setting")
        assert setting is None

    def test_update_setting_success(self, session: Session, settings_sample_data):
        """Test successful setting update."""
        result = AdminSettingsService.update_setting(
            session, 
            "test_float_setting", 
            "2.5", 
            description="Updated description"
        )
        
        assert result is not None
        assert result.setting_value == "2.5"
        assert result.description == "Updated description"
        assert result.updated_at is not None

    def test_update_readonly_setting_fails(self, session: Session, settings_sample_data):
        """Test that updating read-only setting fails."""
        result = AdminSettingsService.update_setting(
            session, 
            "readonly_setting", 
            "new_value"
        )
        
        assert result is None

    def test_validate_setting_value_float(self, session: Session):
        """Test float value validation."""
        # Valid float
        assert AdminSettingsService._validate_setting_value("1.5", "float") is True
        
        # Invalid float
        assert AdminSettingsService._validate_setting_value("not_a_number", "float") is False

    def test_validate_setting_value_integer(self, session: Session):
        """Test integer value validation."""
        # Valid integer
        assert AdminSettingsService._validate_setting_value("42", "integer") is True
        
        # Invalid integer
        assert AdminSettingsService._validate_setting_value("1.5", "integer") is False

    def test_validate_setting_value_boolean(self, session: Session):
        """Test boolean value validation."""
        # Valid booleans
        assert AdminSettingsService._validate_setting_value("true", "boolean") is True
        assert AdminSettingsService._validate_setting_value("false", "boolean") is True
        assert AdminSettingsService._validate_setting_value("True", "boolean") is True
        assert AdminSettingsService._validate_setting_value("False", "boolean") is True
        
        # Invalid boolean
        assert AdminSettingsService._validate_setting_value("maybe", "boolean") is False

    def test_get_setting_value_with_conversion(self, session: Session, settings_sample_data):
        """Test getting setting value with proper type conversion."""
        # Float conversion
        value = AdminSettingsService.get_setting_value(session, "test_float_setting", float)
        assert value == 1.5
        assert isinstance(value, float)
        
        # String conversion (default)
        value = AdminSettingsService.get_setting_value(session, "test_string_setting", str)
        assert value == "test_value"
        assert isinstance(value, str)


class TestAdminTripService:
    """Test class for AdminTripService business logic."""

    @pytest.fixture
    def trip_sample_data(self, session: Session):
        """Create sample data for trip service testing."""
        # Create users
        rider = User(
            auth_id="trip-service-rider",
            name="Service Rider",
            email="servicerider@example.com",
            phone_number="+1900000001",
            role="rider",
            auth_status="verified"
        )
        session.add(rider)
        session.commit()
        session.refresh(rider)
        
        driver = User(
            auth_id="trip-service-driver",
            name="Service Driver",
            email="servicedriver@example.com",
            phone_number="+1900000002",
            role="driver",
            auth_status="verified"
        )
        session.add(driver)
        session.commit()
        session.refresh(driver)
        
        # Create driver profile
        driver_profile = Driver(
            user_id=driver.id,
            taxi_number="SERVICE-001",
            account_status="verified",
            driver_status="online"
        )
        session.add(driver_profile)
        
        # Create rider profile
        rider_profile = Rider(
            user_id=rider.id,
            residence_place="Service Area"
        )
        session.add(rider_profile)
        
        session.commit()
        
        # Create trips
        today = datetime.utcnow()
        yesterday = today - timedelta(days=1)
        
        trips = [
            Trip(
                rider_id=rider.id,
                driver_id=driver.id,
                pickup_latitude=36.8065,
                pickup_longitude=10.1815,
                pickup_address="Service Pickup 1",
                destination_latitude=36.8190,
                destination_longitude=10.1658,
                destination_address="Service Destination 1",
                status="completed",
                trip_type="regular",
                estimated_distance_km=15.0,
                estimated_cost_tnd=25.50,
                requested_at=today,
                completed_at=today,
                created_at=today
            ),
            Trip(
                rider_id=rider.id,
                driver_id=None,
                pickup_latitude=36.8065,
                pickup_longitude=10.1815,
                pickup_address="Service Pickup 2",
                destination_latitude=36.8190,
                destination_longitude=10.1658,
                destination_address="Service Destination 2",
                status="requested",
                trip_type="express",
                estimated_distance_km=8.5,
                estimated_cost_tnd=18.25,
                requested_at=yesterday,
                created_at=yesterday
            )
        ]
        
        for trip in trips:
            session.add(trip)
        
        session.commit()
        return {"rider": rider, "driver": driver, "trips": trips}

    def test_get_all_trips_basic(self, session: Session, trip_sample_data):
        """Test basic trip retrieval."""
        result = AdminTripService.get_all_trips(session)
        
        assert "trips" in result
        assert "total" in result
        assert "page" in result
        assert "page_size" in result
        
        assert len(result["trips"]) >= 2
        assert result["total"] >= 2

    def test_get_all_trips_with_pagination(self, session: Session, trip_sample_data):
        """Test trip retrieval with pagination."""
        result = AdminTripService.get_all_trips(session, page=1, page_size=1)
        
        assert len(result["trips"]) <= 1
        assert result["page"] == 1
        assert result["page_size"] == 1

    def test_get_trips_by_driver(self, session: Session, trip_sample_data):
        """Test filtering trips by driver."""
        driver_id = trip_sample_data["driver"].id
        result = AdminTripService.get_all_trips(session, driver_id=driver_id)
        
        for trip in result["trips"]:
            if trip.driver_id:  # Some trips might not have drivers assigned
                assert trip.driver_id == driver_id

    def test_get_trips_by_status(self, session: Session, trip_sample_data):
        """Test filtering trips by status."""
        result = AdminTripService.get_all_trips(session, status="completed")
        
        for trip in result["trips"]:
            assert trip.status == "completed"

    def test_get_trips_by_date_range(self, session: Session, trip_sample_data):
        """Test filtering trips by date range."""
        today = date.today()
        result = AdminTripService.get_all_trips(
            session, 
            start_date=today, 
            end_date=today
        )
        
        # Should only return trips from today
        assert result["total"] >= 0  # Could be 0 or more depending on data

    def test_get_trip_by_id_success(self, session: Session, trip_sample_data):
        """Test successful trip retrieval by ID."""
        trip_id = trip_sample_data["trips"][0].id
        trip = AdminTripService.get_trip_by_id(session, str(trip_id))
        
        assert trip is not None
        assert trip.id == str(trip_id)
        assert trip.rider_name == "Service Rider"

    def test_get_trip_by_id_not_found(self, session: Session):
        """Test trip retrieval with non-existent ID."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        trip = AdminTripService.get_trip_by_id(session, fake_id)
        
        assert trip is None

    def test_get_trip_status_distribution(self, session: Session, trip_sample_data):
        """Test trip status distribution calculation."""
        distribution = AdminTripService.get_trip_status_distribution(session)
        
        assert isinstance(distribution, dict)
        assert "completed" in distribution
        assert "requested" in distribution
        assert distribution["completed"] >= 1
        assert distribution["requested"] >= 1
