# -*- coding: utf-8 -*-
"""
Vedirect unittest class.

Use pytest package.
"""
import pytest
from vedirect_m8.vedirect import Vedirect
from vedirect_m8.serconnect import SerialConnection
from ve_utils.utils import UType as Ut
from vedirect_m8.exceptions import SettingInvalidException, InputReadException, TimeoutException, VedirectException


class TestVedirect:

    def setup_method(self):
        """
        Setup any state tied to the execution of the given function.

        Invoked for every test function in the module.
        """
        conf = {
            'serial_port': "/tmp/vmodem1",
            'baud': 19200,
            'timeout': 0,
        }

        if not SerialConnection.is_serial_port_exists("/tmp/vmodem1"):
            conf.update(
                {'serial_port': SerialConnection.get_virtual_home_serial_port("vmodem1")}
            )
        self.obj = Vedirect(**conf)

    def test_settings(self):
        """Test configuration settings from Vedirect constructor"""
        assert self.obj.is_serial_ready()
        assert self.obj.is_ready()
        assert self.obj.has_serial_com()
        assert self.obj.connect_to_serial()

    def test_is_serial_com(self):
        """Test is_serial_com method"""
        assert Vedirect.is_serial_com(self.obj._com)
        assert not Vedirect.is_serial_com(dict())
        assert not Vedirect.is_serial_com(None)

    def test_is_timeout(self):
        """Test is_timeout method"""
        assert Vedirect.is_timeout(elapsed=59, timeout=60)
        with pytest.raises(TimeoutException):
            Vedirect.is_timeout(elapsed=60, timeout=60)
            Vedirect.is_timeout(elapsed=102, timeout=60)

    def test_init_serial_connection_from_object(self):
        """Test init_serial_connection_from_object method"""
        obj = self.obj._com
        assert self.obj.init_serial_connection_from_object(obj)

        # test with bad serial port format
        obj = SerialConnection(
            serial_port="/etc/bad_port",
            source_name="TestVedirect"
        )
        with pytest.raises(SettingInvalidException):
            self.obj.init_serial_connection_from_object(obj)

        # test with bad serial port connection
        obj = SerialConnection(
            serial_port="/tmp/vmodem255",
            source_name="TestVedirect"
        )
        with pytest.raises(VedirectException):
            self.obj.init_serial_connection_from_object(obj)

    def test_init_serial_connection(self):
        """Test init_serial_connection method"""
        assert self.obj.init_serial_connection(serial_port=self.obj._com._serial_port,
                                               source_name="TestVedirect"
                                               )

        # test with bad serial port format
        with pytest.raises(SettingInvalidException):
            self.obj.init_serial_connection(serial_port="/etc/bad_port",
                                            source_name="TestVedirect"
                                            )

        # test with bad serial port connection
        with pytest.raises(VedirectException):
            self.obj.init_serial_connection(serial_port="/tmp/vmodem255",
                                            source_name="TestVedirect"
                                            )

    def test_init_settings(self):
        """Test init_settings method"""
        assert self.obj.init_settings(serial_port=self.obj._com._serial_port,
                                      source_name="TestVedirect"
                                      )

        # test with bad serial port format
        with pytest.raises(SettingInvalidException):
            self.obj.init_settings(serial_port="/etc/bad_port",
                                   source_name="TestVedirect"
                                   )

        # test with bad serial port connection
        with pytest.raises(VedirectException):
            self.obj.init_settings(serial_port="/tmp/vmodem255",
                                   source_name="TestVedirect"
                                   )

    def test_init_data_read(self):
        """Test init_data_read method"""
        self.obj.read_data_single()
        assert Ut.is_dict_not_empty(self.obj.dict)
        self.obj.init_data_read()
        assert not Ut.is_dict_not_empty(self.obj.dict) and Ut.is_dict(self.obj.dict)

    def test_input_read(self):
        """Test input_read method"""
        datas = [
            b'\r', b'\n', b'P', b'I', b'D', b'\t',
            b'O', b'x', b'0', b'3', b'\r',
        ]
        [self.obj.input_read(x) for x in datas]
        assert Ut.is_dict_not_empty(self.obj.dict) and self.obj.dict.get('PID') == "Ox03"
        self.obj.init_data_read()
        datas = [
            b'\r', b'\n', b'C', b'h', b'e', b'c', b'k', b's', b'u', b'm', b'\t',
            b'O', b'\r', b'\n', b'\t', 'helloWorld'
        ]
        with pytest.raises(InputReadException):
            [self.obj.input_read(x) for x in datas]

    def test_read_data_single(self):
        """Test read_data_single method"""
        data = self.obj.read_data_single()
        assert Ut.is_dict_not_empty(data)

    def test_read_data_callback(self):
        """Test read_data_callback method"""

        def func_callback(data: dict or None):
            """Callback function"""
            assert Ut.is_dict_not_empty(data)

        self.obj.read_data_callback(callback_function=func_callback,
                                    timeout=20,
                                    max_loops=1
                                    )

        with pytest.raises(TimeoutException):
            self.obj.read_data_callback(callback_function=func_callback,
                                        timeout=0.1,
                                        max_loops=1
                                        )

        with pytest.raises(VedirectException):
            self.obj._com = None
            self.obj.read_data_callback(callback_function=func_callback,
                                        timeout=20,
                                        max_loops=1
                                        )
