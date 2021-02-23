from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import ITModel, Rack, Asset
from contextlib import contextmanager
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

"""Used in class AssetTest(TestCase)"""


class ITModelTest(TestCase):
    """
    Test cases for the ITModel param, display_color
    Reqs: optional; 6-digit, 3-byte hex triplet (RGB) preceded by a pound sign
    (#); case insensitive; e.g. #7FFFD4, #7fffd4
    """
    def test_ITModel_display_color(self):
        display_color_test1 = ITModel(
            vendor="Test Vendor",
            model_number="TestModelNum",
            height=1,
            display_color="#AAA"  # Should NOT throw error
        )
        display_color_test1.full_clean()  # Should NOT throw error

        display_color_test2 = ITModel(
            vendor="Test Vendor",
            model_number="TestModelNum",
            height=1,
            display_color="#AAAA"  # Should throw error
        )
        with self.assertRaises(ValidationError):
            display_color_test2.full_clean()  # Should throw error

        display_color_test3 = ITModel(
            vendor="Test Vendor",
            model_number="TestModelNum",
            height=1,
            display_color="AAA"  # Should throw error
        )
        with self.assertRaises(ValidationError):
            display_color_test3.full_clean()  # Should throw error

        display_color_test4 = ITModel(
            vendor="Test Vendor",
            model_number="TestModelNum",
            height=1,
            display_color="#!!!"  # Should throw error
        )
        with self.assertRaises(ValidationError):
            display_color_test4.full_clean()  # Should throw error

    """
    Test cases for the ITModel param, ethernet_ports
    Reqs: optional, non-negative
    """
    def test_ITModel_ethernet_ports(self):
        ethernet_ports_test1 = ITModel(
            vendor="Test Vendor",
            model_number="TestModelNum",
            height=1,
            ethernet_ports=1  # Should NOT throw error
        )
        ethernet_ports_test1.full_clean()  # Should NOT throw error

        ethernet_ports_test2 = ITModel(
            vendor="Test Vendor",
            model_number="TestModelNum",
            height=1,
            ethernet_ports=-1  # Should throw error
        )
        with self.assertRaises(ValidationError):
            ethernet_ports_test2.full_clean()  # Should throw error

    """
    Test cases for the ITModel param, power_ports
    Reqs: optional, non-negative
    """
    def test_ITModel_power_ports(self):
        power_ports_test1 = ITModel(
            vendor="Test Vendor",
            model_number="TestModelNum",
            height=1,
            power_ports=1  # Should NOT throw error
        )
        power_ports_test1.full_clean()  # Should NOT throw error

        power_ports_test2 = ITModel(
            vendor="Test Vendor",
            model_number="TestModelNum",
            height=1,
            power_ports=-1  # Should throw error
        )
        with self.assertRaises(ValidationError):
            power_ports_test2.full_clean()  # Should throw error

    """
    Test cases for the ITModel param, memory
    Reqs: optional, non-negative
    """
    def test_ITModel_memory(self):
        memory_test1 = ITModel(
            vendor="Test Vendor",
            model_number="TestModelNum",
            height=1,
            memory=16  # Should NOT throw error
        )
        memory_test1.full_clean()  # Should NOT throw error

        memory_test2 = ITModel(
            vendor="Test Vendor",
            model_number="TestModelNum",
            height=1,
            memory=-1  # Should throw error
        )
        with self.assertRaises(ValidationError):
            memory_test2.full_clean()  # Should throw error


class RackTest(TestCase):
    """
    Test cases for the Rack params, row number
    Reqs: required always; string; the address of a rack is by a row letter (A-Z) and
    rack number (positive integer); there is no separator between the row letter and rack number
    """
    def test_Rack(self):
        rack_test1 = Rack(
            rack="A1"
        )
        rack_test1.full_clean()  # Should NOT throw error

        rack_test2 = Rack(
            rack="AA1"
        )
        rack_test2.full_clean()  # Should NOT throw error

        row_test3 = Rack(
            rack="A A1"
        )
        with self.assertRaises(ValidationError):
            row_test3.full_clean()  # Should throw error

        rack_test4 = Rack(
            rack="11"
        )
        with self.assertRaises(ValidationError):
            rack_test4.full_clean()  # Should throw error

        rack_test5 = Rack(
            rack="A-1"
        )
        with self.assertRaises(ValidationError):
            rack_test5.full_clean()  # Should throw error

        rack_test6 = Rack(
            rack="AA"
        )
        with self.assertRaises(ValidationError):
            rack_test6.full_clean()  # Should throw error


class AssetTest(TestCase):
    def setUp(self):
        ITModel.objects.create(
            id=0,
            vendor="Test Vendor",
            model_number="TestModelNum",
            height=1)

        Rack.objects.create(id=0, rack="A1")

    # Test cases for the Asset param, hostname
    # Reqs:  required always; RFC-1034-compliant string

    def test_Asset_hostname(self):
        model = ITModel.objects.get(id=0)
        rack = Rack.objects.get(id=0)

        hostname_test1 = Asset(
            itmodel=model,
            hostname="test",  # Should NOT throw error
            rack=rack,
            rack_position=1
        )
        hostname_test1.full_clean()  # Should NOT throw error

        hostname_test2 = Asset(
            itmodel=model,
            hostname="!",  # Should throw error
            rack=rack,
            rack_position=1
        )
        with self.assertRaises(ValidationError):
            hostname_test2.full_clean()  # Should throw error


    # Test cases for the Asset param, rack_position
    # Reqs: required always; positive integer; refers to the vertical location
    # (on a rack, measured in U) from the bottom of the equipment

    def test_Asset_rack_position(self):
        model = ITModel.objects.get(id=0)
        rack = Rack.objects.get(id=0)

        rack_pos_test1 = Asset(
            itmodel=model,
            hostname="test",
            rack=rack,
            rack_position=1  # Should NOT throw error
        )
        rack_pos_test1.full_clean()  # Should NOT throw error

        rack_pos_test2 = Asset(
            itmodel=model,
            hostname="test",
            rack=rack,
            rack_position=-1  # Should throw error
        )
        with self.assertRaises(ValidationError):
            rack_pos_test2.full_clean()  # Should throw error
