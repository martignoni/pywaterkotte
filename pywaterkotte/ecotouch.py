""" pyecotouch main module"""
from typing import (
    Any,
    Callable,
    Collection,
    NamedTuple,
    Sequence,
    Tuple,
    List,
)  # , List

# from unittest import case
import re
import math
from enum import Enum
from datetime import datetime, timedelta
import struct
import logging
# import requests


# import random
import aiohttp

MAX_NO_TAGS = 10
_LOGGER: logging.Logger = None

# def setup_logger():
#     global _LOGGER
#     _LOGGER = logging.getLogger(__name__)

# setup_logger()

class StatusException(Exception):
    """A Status Exception."""

    # pass


class InvalidResponseException(Exception):
    """A InvalidResponseException."""

    # pass


class InvalidValueException(Exception):
    """A InvalidValueException."""

    # pass


class EcotouchTag:
    """A Dummy Class."""

    # pass



def _to_float(int_value):
    # Use struct to interpret the integer as a float
    return struct.unpack('!f', struct.pack('!I', int_value))[0]

def _rshift(val, n): return val>>n if val >= 0 else (val+0x100000000)>>n

def _process_analogs(
    self: EcotouchTag, vals, bitnum=None, *other_args
):  # pylint: disable=unused-argument,keyword-arg-before-vararg
    #(a1, a2):
    assert len(self.tags) == 2
    assert self.tags[0][0] in ["A"]
    assert self.tags[1][0] in ["A"]
    if self.tags[0] not in vals or self.tags[1] not in vals:
        return None

    #print(vals[self.tags[0]])
    #print(vals[self.tags[1]])
    a1=int(vals[self.tags[0]])
    a2=int(vals[self.tags[1]])

    # Combine the two 16-bit values into one 32-bit integer
    #i32 = (a1 << 16) | a2
    i32 = _rshift((a1 << 16),0)| _rshift(a2,0) & 65535
    #print(i32)
    # Convert the 32-bit integer to a float
    rval = _to_float(i32)
    # Round to 1 decimal place
    rval = round(rval, 1)
    #print("rval", rval)

    return rval

# default method that reads a value based on a single tag
def _parse_value_default(
    self: EcotouchTag, vals, bitnum=None, *other_args
):  # pylint: disable=unused-argument,keyword-arg-before-vararg
    assert len(self.tags) == 1
    ecotouch_tag = self.tags[0]
    assert ecotouch_tag[0] in ["A", "I", "D"]

    if ecotouch_tag not in vals:
        return None

    val = vals[ecotouch_tag]

    if ecotouch_tag[0] == "A":
        return float(val) / 10.0
    if ecotouch_tag[0] == "I":
        if bitnum is None:
            return int(val)
        else:
            return (int(val) & (1 << bitnum)) > 0

    if ecotouch_tag[0] == "D":
        if val == "1":
            return True
        elif val == "0":
            return False
        else:
            raise InvalidValueException(
                # "%s is not a valid value for %s" % (val, ecotouch_tag)
                f"{val} is not a valid value for {ecotouch_tag}"
            )
    return None


def _write_value_default(self, value, et_values):
    _LOGGER.debug(f"_write_value_default, value: {value}, et_values: {et_values}")
    assert len(self.tags) == 1
    ecotouch_tag = self.tags[0]
    assert ecotouch_tag[0] in ["A", "I", "D"]

    if ecotouch_tag[0] == "I":
        assert isinstance(value, int)
        et_values[ecotouch_tag] = str(value)
    elif ecotouch_tag[0] == "D":
        assert isinstance(value, bool)
        et_values[ecotouch_tag] = "1" if value else "0"
    elif ecotouch_tag[0] == "A":
        assert isinstance(value, float)
        et_values[ecotouch_tag] = str(int(value * 10))


def _parse_series(self, e_vals, *other_args):  # pylint: disable=unused-argument
    # pylint: disable=invalid-name,line-too-long
    aI105 = [
        "Custom",
        "Ai1",
        "Ai1+",
        "AiQE",
        "DS 5023",
        "DS 5027Ai",
        "DS 5051",
        "DS 5050T",
        "DS 5110T",
        "DS 5240",
        "DS 6500",
        "DS 502xAi",
        "DS 505x",
        "DS 505xT",
        "DS 51xxT",
        "DS 509x",
        "DS 51xx",
        "EcoTouch Ai1 Geo",
        "EcoTouch DS 5027 Ai",
        "EnergyDock",
        "Basic Line Ai1 Geo",
        "EcoTouch DS 5018 Ai",
        "EcoTouch DS 5050T",
        "EcoTouch DS 5112.5 DT",
        "EcoTouch 5029 Ai",
        "DS 6500 D (Duo)",
        "ET 6900 Q",
        "EcoTouch Geo Inverter",
        "EcoTouch 5110TWR",
        "EcoTouch 5240TWR",
        "EcoTouch 5240T",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "Ai QL / WP QL",
        "WPQL-K",
        "EcoTouch Ai1 Air",
        "EcoTouch Ai1 Air",
        "EcoTouch MB 7010",
        "EcoTouch DA 5018 Ai",
        "EcoTouch Air LCI",
        "EcoTouch Ai1 Air K1.1",
        "EcoTouch DA 5018 Ai K1.1",
        "EcoTouch Ai1 Air K2",
        "EcoTouch DA 5018 Ai K2",
        "EcoTouch Ai1 Air 2018",
        "Basic Line Ai1 Air",
        "Basic Line Split",
        "Basic Line Split W",
        "EcoTouch Ai1 Air LC S",
        "EcoTouch Air Kaskade",
        "EcoTouch Ai1 Air K1.2",
        "EcoTouch DA 5018 Ai K1.2",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    ]
    return aI105[int(e_vals["I105"])] if e_vals["I105"] else ""


def _parse_bios(self, e_vals, *other_args):  # pylint: disable=unused-argument
    return f"{str(e_vals['I3'])[0]}.{str(e_vals['I3'])[1:3]}"


def _parse_fw(self, e_vals, *other_args):  # pylint: disable=unused-argument
    return f"0{str(e_vals['I1'])[0]}.{str(e_vals['I1'])[1:3]}.{str(e_vals['I1'])[3:]}-{str(e_vals['I2'])}"  # pylint: disable=line-too-long


def _parse_id(self, e_vals, *other_args):  # pylint: disable=unused-argument
    # pylint: disable=invalid-name,line-too-long
    aI110 = [
        "Ai1 5005.4",
        "Ai1 5006.4",
        "Ai1 5007.4",
        "Ai1 5008.4",
        "Ai1+ 5006.3",
        "Ai1+ 5007.3",
        "Ai1+ 5009.3",
        "Ai1+ 5011.3",
        "Ai1+ 5006.3 (1x230V)",
        "Ai1+ 5007.3 (1x230V)",
        "Ai1+ 5009.3 (1x230V)",
        "Ai1+ 5011.3 (1x230V)",
        "DS 5006.3",
        "DS 5008.3",
        "DS 5009.3",
        "DS 5011.3",
        "DS 5014.3",
        "DS 5017.3",
        "DS 5020.3",
        "DS 5023.3",
        "DS 5006.3 (1x230V)",
        "DS 5008.3 (1x230V)",
        "DS 5009.3 (1x230V)",
        "DS 5011.3 (1x230V)",
        "DS 5014.3 (1x230V)",
        "DS 5017.3 (1x230V)",
        "DS 5006.4",
        "DS 5008.4",
        "DS 5009.4",
        "DS 5011.4",
        "DS 5014.4",
        "DS 5017.4",
        "DS 5020.4",
        "DS 5023.4",
        "DS 5007.3 Ai",
        "DS 5009.3 Ai",
        "DS 5010.3 Ai",
        "DS 5012.3 Ai",
        "DS 5015.3 Ai",
        "DS 5019.3 Ai",
        "DS 5022.3 Ai",
        "DS 5025.3 Ai",
        "DS 5007.3 Ai (1x230V)",
        "DS 5009.3 Ai (1x230V)",
        "DS 5010.3 Ai (1x230V)",
        "DS 5012.3 Ai (1x230V)",
        "DS 5015.3 Ai (1x230V)",
        "DS 5019.3 Ai (1x230V)",
        "DS 5007.4 Ai",
        "DS 5009.4 Ai",
        "DS 5010.4 Ai",
        "DS 5012.4 Ai",
        "DS 5015.4 Ai",
        "DS 5019.4 Ai",
        "DS 5022.4 Ai",
        "DS 5025.4 Ai",
        "DS 5007.4 Ai (1x230V)",
        "DS 5009.4 Ai (1x230V)",
        "DS 5010.4 Ai (1x230V)",
        "DS 5012.4 Ai (1x230V)",
        "DS 5015.4 Ai (1x230V)",
        "DS 5030.3",
        "DS 5034.3",
        "DS 5043.3",
        "DS 5051.3",
        "DS 5030.4",
        "DS 5034.4",
        "DS 5043.4",
        "DS 5051.4",
        "DS 5030.3 T",
        "DS 5037.3 T",
        "DS 5044.3 T",
        "DS 5050.3 T",
        "DS 5030.4 T",
        "DS 5037.4 T",
        "DS 5044.4 T",
        "DS 5050.4 T",
        "DS 5062.3 T",
        "DS 5072.3 T",
        "DS 5089.3 T",
        "DS 5109.3 T",
        "DS 5062.4 T",
        "DS 5072.4 T",
        "DS 5089.4 T",
        "DS 5109.4 T",
        "DS 5118.3",
        "DS 5136.3",
        "DS 5161.3",
        "DS 5162.3",
        "DS 5193.3",
        "DS 5194.3",
        "DS 5231.3",
        "DS 5118.4",
        "DS 5136.4",
        "DS 5161.4",
        "DS 5162.4",
        "DS 5194.4",
        "DS 6237.3",
        "DS 6271.3",
        "DS 6299.3",
        "DS 6388.3",
        "DS 6438.3",
        "DS 6485.3",
        "DS 6237.4",
        "DS 6271.4",
        "DS 6299.4",
        "DS 6388.4",
        "DS 6438.4",
        "DS 6485.4",
        "Ai1QE 5006.5",
        "Ai1QE 5007.5",
        "Ai1QE 5009.5",
        "Ai1QE 5010.5",
        "Ai1QE 5006.5 (1x230V)",
        "Ai1QE 5007.5 (1x230V)",
        "Ai1QE 5009.5 (1x230V)",
        "Ai1QE 5010.5 (1x230V)",
        "DS 5008.5AI",
        "DS 5009.5AI",
        "DS 5012.5AI",
        "DS 5014.5AI",
        "DS 5017.5AI",
        "DS 5020.5AI",
        "DS 5023.5AI",
        "DS 5026.5AI",
        "DS 5008.5AI (1x230V)",
        "DS 5009.5AI (1x230V)",
        "DS 5012.5AI (1x230V)",
        "DS 5014.5AI (1x230V)",
        "DS 5017.5AI (1x230V)",
        "DS 5029.5",
        "DS 5033.5",
        "DS 5040.5",
        "DS 5045.5",
        "DS 5050.5",
        "DS 5059.5",
        "DS 5028.5 T",
        "DS 5034.5 T",
        "DS 5040.5 T",
        "DS 5046.5 T",
        "DS 5052.5 T",
        "DS 5058.5 T",
        "DS 5063.5 T",
        "DS 5075.5 T",
        "DS 5085.5 T",
        "DS 5095.5 T",
        "DS 5112.5 T",
        "DS 5076.5",
        "DS 5095.5",
        "DS 5123.5",
        "DS 5158.5",
        "Ai QL",
        "Ai QL Kaskade",
        "DS 5013.5AI",
        "DS 5013.5AI (1x230V)",
        "DS 5036.4T",
        "DS 5049.4T",
        "DS 5063.4T",
        "DS 5077.4T",
        "DS 5007.5AI HT",
        "DS 5008.5AI HT",
        "DS 5010.5AI HT",
        "DS 5014.5AI HT",
        "DS 5018.5AI HT",
        "DS 5023.5AI HT",
        "DS 5007.5AI HT (1x230V)",
        "DS 5008.5AI HT (1x230V)",
        "DS 5010.5AI HT (1x230V)",
        "DS 5014.5AI HT (1x230V)",
        "DS 5018.5AI HT (1x230V)",
        "DS 5005.4Ai HT",
        "DS 5007.4Ai HT",
        "DS 5009.4Ai HT",
        "DS 5010.4Ai HT",
        "DS 5012.4Ai HT",
        "DS 5015.4Ai HT",
        "DS 5005.4Ai HT (1x230V)",
        "DS 5007.4Ai HT (1x230V)",
        "DS 5009.4Ai HT (1x230V)",
        "DS 5010.4Ai HT (1x230V)",
        "5006.5",
        "5008.5",
        "5010.5",
        "5013.5",
        "5006.5(1x230V)",
        "5008.5(1x230V)",
        "5010.5(1x230V)",
        "5013.5(1x230V)",
        "EcoTouch Ai1 QL ",
        "5018.5",
        "5010.5",
        "5010.5",
        "DS 5008.5AI",
        "DS 5010.5AI",
        "DS 5012.5AI",
        "DS 5014.5AI",
        "DS 5017.5AI",
        "DS 5020.5AI",
        "DS 5023.5AI",
        "DS 5027.5AI",
        "DS 5008.5AI (1x230V)",
        "DS 5010.5AI (1x230V)",
        "DS 5012.5AI (1x230V)",
        "DS 5014.5AI (1x230V)",
        "DS 5017.5AI (1x230V)",
        "Power+",
        "DS 5145.5 Tandem",
        "DS 5150.5",
        "DS 5182.5 Tandem",
        "DS 5226.5",
        "DS 5235.5 Tandem",
        "DS 6272.5 Trio",
        "DS 6300.5 Tandem",
        "DS 6352.5 Trio",
        "DS 6450.5 Trio",
        "5005.5",
        "5006.5",
        "5007.5",
        "5008.5",
        "5010.5",
        "5005.5 (1x230V)",
        "5006.5 (1x230V)",
        "5008.5 (1x230V)",
        "5010.5 (1x230V)",
        "DS 5006.5Ai Split",
        "DS 5007.5Ai Split",
        "DS 5009.5Ai Split",
        "DS 5012.5Ai Split",
        "DS 5015.5Ai Split",
        "DS 5020.5Ai Split",
        "DS 5025.5Ai Split",
        "DS 5006.3Ai Split",
        "DS 5007.3Ai Split",
        "DS 5008.3Ai Split",
        "DS 5010.3Ai Split",
        "DS 5012.3Ai Split",
        "DS 5015.3Ai Split",
        "DS 5018.3Ai Split",
        "DS 5020.3Ai Split",
        "5008.5",
        "5011.5",
        "5014.5",
        "5018.5",
        "5008.5 (230V)",
        "5011.5 (230V)",
        "5014.5 (230V)",
        "5018.5 (230V)",
        "5018.5",
        "5010.5",
        "5034.5T",
        "5045.5T",
        "5056.5T",
        "5009.3",
        "5068.5 DT",
        "5090.5 DT",
        "5112.5 DT",
        "5007.3",
        "5011.3",
        "EcoTouch 5007.5Ai",
        "EcoTouch 5008.5Ai",
        "EcoTouch 5010.5Ai",
        "EcoTouch 5014.5Ai",
        "EcoTouch 5018.5Ai",
        "EcoTouch 5023.5Ai",
        "EcoTouch 5029.5Ai",
        "EcoTouch 5007.5Ai",
        "EcoTouch 5008.5Ai",
        "EcoTouch 5010.5Ai",
        "EcoTouch 5014.5Ai",
        "EcoTouch 5018.5Ai",
        "DS 5028.4T HT",
        "EcoTouch compact 5004.5",
        "5010.5",
        "5010.5",
        "DS 6450.5 D",
        "5028.5T",
        "ET 6600.5 Q",
        "ET 6750.5 Q",
        "ET 6900.5 Q",
        "5015.5 Ai",
        "5010.5 Ai",
        "5010.5",
        "5018.5",
        "5010.5(1x230V)",
        "5018.5(1x230V)",
        "5010.5",
        "5018.5",
        "5010.5(1x230V)",
        "5018.5(1x230V)",
        "50xx.5",
        "5003.5 Ai",
        "5004.5(1x230V)",
        "",
        "5008.5(1x230V)",
        "5011.5(1x230V)",
        "5012.5(1x230V)",
        "",
        "5011.5",
        "5012.5",
        "5015.5",
        "5003.5 Ai NX",
        "5004.5(1x230V)",
        "",
        "5008.5(1x230V)",
        "5011.5(1x230V)",
        "5012.5(1x230V)",
        "",
        "5011.5",
        "5012.5",
        "5015.5",
        "5004.5(1x230V)",
        "",
        "5008.5(1x230V)",
        "5011.5(1x230V)",
        "5012.5(1x230V)",
        "",
        "5011.5",
        "5012.5",
        "5015.5",
        "5004.5(1x230V)",
        "",
        "5008.5(1x230V)",
        "5011.5(1x230V)",
        "5012.5(1x230V)",
        "",
        "5011.5",
        "5012.5",
        "5015.5",
        "EcoTouch Air Kaskade",
        "5003.6 Ai NX",
        "5003.5 Ai SNB",
        "5003.6 Ai SVB",
        "5010.5-18 (230V)",
        "5010.5-18 (230V)",
        "5018.5",
        "5018.5(1x230V)",
        "5018.5",
        "5018.5(1x230V)",
        "EcoTouch 5007.5Ai Split",
        "EcoTouch 5008.5Ai Split",
        "EcoTouch 5010.5Ai Split",
        "EcoTouch 5014.5Ai Split",
        "EcoTouch 5018.5Ai Split",
        "EcoTouch 5023.5Ai Split",
        "EcoTouch 5029.5Ai Split",
        "ET 5063.4 Tandem WR",
        "ET 5072.4 Tandem WR",
        "ET 5090.4 Tandem WR",
        "ET 5108.4 Tandem WR",
        "ET 5144.4 Tandem WR",
        "ET 5179.4 Tandem WR",
        "ET 5222.4 Tandem WR",
        "ET 5144.4 Tandem",
        "ET 5179.4 Tandem",
        "ET 5222.4 Tandem",
        None,
    ]
    return aI110[int(e_vals["I110"])] if e_vals["I110"] else ""


def _parse_sn(self, e_vals, *other_args):  # pylint: disable=unused-argument
    sn1 = int(e_vals["I114"])
    sn2 = int(e_vals["I115"])
    s1 = "WE" if math.floor(sn1 / 1000) > 0 else "00"  # pylint: disable=invalid-name
    s2 = (
        sn1 - 1000 if math.floor(sn1 / 1000) > 0 else sn1
    )  # pylint: disable=invalid-name
    s2 = "0" + s2 if s2 < 10 else s2  # pylint: disable=invalid-name
    return str(s1) + str(s2) + str(sn2)


def _parse_time(self, e_vals, *other_args):  # pylint: disable=unused-argument
    vals = [int(e_vals[tag]) for tag in self.tags]
    vals[0] = vals[0] + 2000
    next_day = False
    if vals[3] == 24:
        vals[3] = 0
        next_day = True

    dt = datetime(*vals)  # pylint: disable=invalid-name
    return dt + timedelta(days=1) if next_day else dt


def _parse_status(self, value, *other_args):  # pylint: disable=unused-argument
    assert len(self.tags) == 1
    ecotouch_tag = self.tags[0]
    # assert isinstance(value[ecotouch_tag],int)
    if value[ecotouch_tag] == "0":
        return "off"
    elif value[ecotouch_tag] == "1":
        return "on"
    elif value[ecotouch_tag] == "2":
        return "disabled"
    else:
        return "Error"

def _parse_cop_year(self, value, *other_args):  # pylint: disable=unused-argument
    assert len(self.tags) == 1
    ecotouch_tag = self.tags[0]
    # assert isinstance(value[ecotouch_tag],int)
    return int(value[ecotouch_tag]) + 2000

def _parse_state(self, value, *other_args):  # pylint: disable=unused-argument
    assert len(self.tags) == 1
    ecotouch_tag = self.tags[0]
    # assert isinstance(value[ecotouch_tag],int)
    if value[ecotouch_tag] == "0":
        return "off"
    elif value[ecotouch_tag] == "1":
        return "auto"
    elif value[ecotouch_tag] == "2":
        return "manual"
    else:
        return "Error"


def _write_state(self, value, et_values):
    assert len(self.tags) == 1
    ecotouch_tag = self.tags[0]
    assert ecotouch_tag[0] in ["I"]
    if value == "off":
        et_values[ecotouch_tag] = "0"
    elif value == "auto":
        et_values[ecotouch_tag] = "1"
    elif value == "manual":
        et_values[ecotouch_tag] = "2"


def _write_time(tag, value, et_values):
    assert isinstance(value, datetime)
    vals = [
        str(val)
        for val in [
            value.year % 100,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second,
        ]
    ]
    # check if result is the same
    # for i in range(len(tag.tags)):
    #     et_values[tag.tags[i]] = vals[i]
    # print(et_values)
    for i, tags in enumerate(tag.tags):
        et_values[tags] = vals[i]


class TagData(NamedTuple):
    """TagData Class"""

    tags: Collection[str]
    unit: str = None
    writeable: bool = False
    read_function: Callable = _parse_value_default
    write_function: Callable = _write_value_default
    bit: int = None


class EcotouchTag(TagData, Enum):  # pylint: disable=function-redefined
    """EcotouchTag Class"""

    TEMPERATURE_OUTSIDE = TagData(["A1"], "°C")
    HOLIDAY_ENABLED = TagData(["D420"], writeable=True)
    HOLIDAY_START_TIME = TagData(
        ["I1254", "I1253", "I1252", "I1250", "I1251"],
        writeable=True,
        read_function=_parse_time,
        write_function=_write_time,
    )
    HOLIDAY_END_TIME = TagData(
        ["I1259", "I1258", "I1257", "I1255", "I1256"],
        writeable=True,
        read_function=_parse_time,
        write_function=_write_time,
    )
    TEMPERATURE_OUTSIDE_1H = TagData(["A2"], "°C")
    TEMPERATURE_OUTSIDE_24H = TagData(["A3"], "°C")
    TEMPERATURE_SOURCE_IN = TagData(["A4"], "°C")
    TEMPERATURE_SOURCE_OUT = TagData(["A5"], "°C")
    TEMPERATURE_EVAPORATION = TagData(["A6"], "°C")
    TEMPERATURE_SUCTION = TagData(["A7"], "°C")
    PRESSURE_EVAPORATION = TagData(["A8"], "bar")
    TEMPERATURE_RETURN_SET = TagData(["A10"], "°C")
    TEMPERATURE_RETURN = TagData(["A11"], "°C")
    TEMPERATURE_FLOW = TagData(["A12"], "°C")
    TEMPERATURE_CONDENSATION = TagData(["A14"], "°C")
    PRESSURE_CONDENSATION = TagData(["A15"], "bar")
    TEMPERATURE_STORAGE = TagData(["A16"], "°C")
    TEMPERATURE_ROOM = TagData(["A17"], "°C")
    TEMPERATURE_ROOM_1H = TagData(["A18"], "°C")
    TEMPERATURE_WATER = TagData(["A19"], "°C")
    TEMPERATURE_POOL = TagData(["A20"], "°C")
    TEMPERATURE_SOLAR = TagData(["A21"], "°C")
    TEMPERATURE_SOLAR_FLOW = TagData(["A22"], "°C")
    POSITION_EXPANSION_VALVE = TagData(["A23"], "%")
    POWER_COMPRESSOR = TagData(["A25"], "kW")
    POWER_HEATING = TagData(["A26"], "kW")
    POWER_COOLING = TagData(["A27"], "kW")
    COP_HEATING = TagData(["A28"], "COP")
    COP_COOLING = TagData(["A29"], "COP")
    TEMPERATURE_HEATING_RETURN = TagData(["A30"], "°C")
    TEMPERATURE_HEATING_SET = TagData(["A31"], "°C", writeable=True)
    TEMPERATURE_HEATING_SET2 = TagData(["A32"], "°C", writeable=True)
    TEMPERATURE_COOLING_RETURN = TagData(["A33"], "°C")
    TEMPERATURE_COOLING_SET = TagData(["A34"], "°C", writeable=True)
    TEMPERATURE_COOLING_SET2 = TagData(["A35"], "°C", writeable=True)
    TEMPERATURE_WATER_SETPOINT = TagData(["A37"], "°C", writeable=True)
    TEMPERATURE_WATER_SETPOINT2 = TagData(["A38"], "°C", writeable=True)
    TEMPERATURE_POOL_SETPOINT = TagData(["A40"], "°C", writeable=True)
    TEMPERATURE_POOL_SETPOINT2 = TagData(["A41"], "°C", writeable=True)
    TEMPERATURE_MIXING1_CURRENT = TagData(["A44"], "°C")
    TEMPERATURE_MIXING1_SET = TagData(["A45"], "°C", writeable=True)
    TEMPERATURE_MIXING2_CURRENT = TagData(["A46"], "°C")
    TEMPERATURE_MIXING2_SET = TagData(["A47"], "°C", writeable=True)
    TEMPERATURE_MIXING3_CURRENT = TagData(["A48"], "°C")
    TEMPERATURE_MIXING3_SET = TagData(["A49"], "°C", writeable=True)
    COMPRESSOR_POWER = TagData(["A50"], "%")
    PERCENT_HEAT_CIRC_PUMP = TagData(["A51"], "%")
    PERCENT_SOURCE_PUMP = TagData(["A52"], "%")
    PERCENT_COMPRESSOR = TagData(["A58"], "%")
    HYSTERESIS_HEATING = TagData(["A61"], "K")
    TEMPERATURE2_OUTSIDE_1H = TagData(["A90"], "°C")
    NVI_NORM_AUSSEN = TagData(["A91"], "?", writeable=True)
    NVI_HEIZKREIS_NORM = TagData(["A92"], "?", writeable=True)
    NVI_T_HEIZGRENZE = TagData(["A93"], "?°C", writeable=True)
    NVI_T_HEIZGRENZE_SOLL = TagData(["A94"], "?°C", writeable=True)
    MAX_VL_TEMP = TagData(["A95"], "°C", writeable=True)
    TEMP_SET_0_DEG = TagData(["A97"], "°C", writeable=True)
    COOL_ENABLE_TEMP = TagData(["A108"], "°C", writeable=True)
    NVI_SOLL_KUEHLEN = TagData(["A109"], "°C", writeable=True)
    T_HEATING_LIMIT_MIXING1 = TagData(["A276"], writeable=True)
    T_HEATING_LIMIT_TARGET_MIXING1 = TagData(["A277"], writeable=True)
    T_NORM_OUTDOOR_MIXING1 = TagData(["A274"], writeable=True)
    T_NORM_HEATING_CICLE_MIXING1 = TagData(["A275"], writeable=True)
    MAX_TEMP_MIXING1 = TagData(["A278"], writeable=True)
    T_HEATING_LIMIT_MIXING2 = TagData(["A322"], writeable=True)
    T_HEATING_LIMIT_TARGET_MIXING2 = TagData(["A323"], writeable=True)
    T_NORM_OUTDOOR_MIXING2 = TagData(["A320"], writeable=True)
    T_NORM_HEATING_CICLE_MIXING2 = TagData(["A321"], writeable=True)
    MAX_TEMP_MIXING2 = TagData(["A324"], writeable=True)
    T_HEATING_LIMIT_MIXING3 = TagData(["A368"], writeable=True)
    T_HEATING_LIMIT_TARGET_MIXING3 = TagData(["A369"], writeable=True)
    T_NORM_OUTDOOR_MIXING3 = TagData(["A366"], writeable=True)
    T_NORM_HEATING_CICLE_MIXING3 = TagData(["A367"], writeable=True)
    MAX_TEMP_MIXING3 = TagData(["A372"], writeable=True)
    ANUAL_CONSUMPTION_COMPRESSOR = TagData(["A444","A445"],read_function=_process_analogs)
    ANUAL_CONSUMPTION_SOURCEPUMP = TagData(["A446","A447"],read_function=_process_analogs)
    ANUAL_CONSUMPTION_EXTERNALHEATER = TagData(["A448","A449"],read_function=_process_analogs)
    ANUAL_CONSUMPTION_HEATING = TagData(["A452","A453"],read_function=_process_analogs)
    ANUAL_CONSUMPTION_WATER = TagData(["A454","A455"],read_function=_process_analogs)
    ANUAL_CONSUMPTION_POOL = TagData(["A456","A457"],read_function=_process_analogs)
    HEATPUMP_COP = TagData(["A460"])
    TEMPCHANGE_HEATING_PV = TagData(["A682"], "°C")
    TEMPCHANGE_COOLING_PV = TagData(["A683"], "°C")
    TEMPCHANGE_WARMWATER_PV = TagData(["A684"], "°C")
    TEMPCHANGE_POOL_PV = TagData(["A685"], "°C")
    CONSUMPTION_COMPRESSOR1 = TagData(["A782"])
    CONSUMPTION_COMPRESSOR2 = TagData(["A783"])
    CONSUMPTION_COMPRESSOR3 = TagData(["A784"])
    CONSUMPTION_COMPRESSOR4 = TagData(["A785"])
    CONSUMPTION_COMPRESSOR5 = TagData(["A786"])
    CONSUMPTION_COMPRESSOR6 = TagData(["A787"])
    CONSUMPTION_COMPRESSOR7 = TagData(["A788"])
    CONSUMPTION_COMPRESSOR8 = TagData(["A789"])
    CONSUMPTION_COMPRESSOR9 = TagData(["A790"])
    CONSUMPTION_COMPRESSOR10 = TagData(["A791"])
    CONSUMPTION_COMPRESSOR11 = TagData(["A792"])
    CONSUMPTION_COMPRESSOR12 = TagData(["A793"])
    CONSUMPTION_SOURCEPUMP1 = TagData(["A794"])
    CONSUMPTION_SOURCEPUMP2 = TagData(["A795"])
    CONSUMPTION_SOURCEPUMP3 = TagData(["A796"])
    CONSUMPTION_SOURCEPUMP4 = TagData(["A797"])
    CONSUMPTION_SOURCEPUMP5 = TagData(["A798"])
    CONSUMPTION_SOURCEPUMP6 = TagData(["A799"])
    CONSUMPTION_SOURCEPUMP7 = TagData(["A800"])
    CONSUMPTION_SOURCEPUMP8 = TagData(["A802"])
    CONSUMPTION_SOURCEPUMP9 = TagData(["A804"])
    CONSUMPTION_SOURCEPUMP10 = TagData(["A805"])
    CONSUMPTION_SOURCEPUMP11 = TagData(["A806"])
    CONSUMPTION_SOURCEPUMP12 = TagData(["A807"])
    #Docs say it should start at 806 for external heater but there is an overlapp to source pump
    CONSUMPTION_EXTERNALHEATER1 = TagData(["A808"])
    CONSUMPTION_EXTERNALHEATER2 = TagData(["A809"])
    CONSUMPTION_EXTERNALHEATER3 = TagData(["A810"])
    CONSUMPTION_EXTERNALHEATER4 = TagData(["A811"])
    CONSUMPTION_EXTERNALHEATER5 = TagData(["A812"])
    CONSUMPTION_EXTERNALHEATER6 = TagData(["A813"])
    CONSUMPTION_EXTERNALHEATER7 = TagData(["A814"])
    CONSUMPTION_EXTERNALHEATER8 = TagData(["A815"])
    CONSUMPTION_EXTERNALHEATER9 = TagData(["A816"])
    CONSUMPTION_EXTERNALHEATER10 = TagData(["A817"])
    CONSUMPTION_EXTERNALHEATER11 = TagData(["A818"])
    CONSUMPTION_EXTERNALHEATER12 = TagData(["A819"])
    CONSUMPTION_HEATING1 = TagData(["A830"])
    CONSUMPTION_HEATING2 = TagData(["A831"])
    CONSUMPTION_HEATING3 = TagData(["A832"])
    CONSUMPTION_HEATING4 = TagData(["A833"])
    CONSUMPTION_HEATING5 = TagData(["A834"])
    CONSUMPTION_HEATING6 = TagData(["A835"])
    CONSUMPTION_HEATING7 = TagData(["A836"])
    CONSUMPTION_HEATING8 = TagData(["A837"])
    CONSUMPTION_HEATING9 = TagData(["A838"])
    CONSUMPTION_HEATING10 = TagData(["A839"])
    CONSUMPTION_HEATING11 = TagData(["A840"])
    CONSUMPTION_HEATING12 = TagData(["A841"])
    CONSUMPTION_WARMWATER1 = TagData(["A842"])
    CONSUMPTION_WARMWATER2 = TagData(["A843"])
    CONSUMPTION_WARMWATER3 = TagData(["A844"])
    CONSUMPTION_WARMWATER4 = TagData(["A845"])
    CONSUMPTION_WARMWATER5 = TagData(["A846"])
    CONSUMPTION_WARMWATER6 = TagData(["A847"])
    CONSUMPTION_WARMWATER7 = TagData(["A848"])
    CONSUMPTION_WARMWATER8 = TagData(["A849"])
    CONSUMPTION_WARMWATER9 = TagData(["A850"])
    CONSUMPTION_WARMWATER10 = TagData(["A851"])
    CONSUMPTION_WARMWATER11 = TagData(["A852"])
    CONSUMPTION_WARMWATER12 = TagData(["A853"])
    CONSUMPTION_POOL1 = TagData(["A854"])
    CONSUMPTION_POOL2 = TagData(["A855"])
    CONSUMPTION_POOL3 = TagData(["A856"])
    CONSUMPTION_POOL4 = TagData(["A857"])
    CONSUMPTION_POOL5 = TagData(["A858"])
    CONSUMPTION_POOL6 = TagData(["A859"])
    CONSUMPTION_POOL7 = TagData(["A860"])
    CONSUMPTION_POOL8 = TagData(["A861"])
    CONSUMPTION_POOL9 = TagData(["A862"])
    CONSUMPTION_POOL10 = TagData(["A863"])
    CONSUMPTION_POOL11 = TagData(["A864"])
    CONSUMPTION_POOL12 = TagData(["A865"])
    HEATPUMP_COP_MONTH1 = TagData(["A924"])
    HEATPUMP_COP_MONTH2 = TagData(["A925"])
    HEATPUMP_COP_MONTH3 = TagData(["A926"])
    HEATPUMP_COP_MONTH4 = TagData(["A927"])
    HEATPUMP_COP_MONTH5 = TagData(["A928"])
    HEATPUMP_COP_MONTH6 = TagData(["A929"])
    HEATPUMP_COP_MONTH7 = TagData(["A930"])
    HEATPUMP_COP_MONTH8 = TagData(["A930"])
    HEATPUMP_COP_MONTH9 = TagData(["A931"])
    HEATPUMP_COP_MONTH10 = TagData(["A932"])
    HEATPUMP_COP_MONTH11 = TagData(["A933"])
    HEATPUMP_COP_MONTH12 = TagData(["A934"])
    HEATINGMODE_MIXING1 = TagData(["D251"])
    HEATINGMODE_MIXING2 = TagData(["D294"])
    HEATINGMODE_MIXING3 = TagData(["D337"])
    VERSION_CONTROLLER = TagData(
        ["I1", "I2"],
        writeable=False,
        read_function=_parse_fw,
    )
    # VERSION_CONTROLLER_BUILD = TagData(["I2"])
    VERSION_BIOS = TagData(["I3"], writeable=False, read_function=_parse_bios)
    DATE_DAY = TagData(["I5"])
    DATE_MONTH = TagData(["I6"])
    DATE_YEAR = TagData(["I7"])
    TIME_HOUR = TagData(["I8"])
    TIME_MINUTE = TagData(["I9"])
    OPERATING_HOURS_COMPRESSOR_1 = TagData(["I10"])
    OPERATING_HOURS_COMPRESSOR_2 = TagData(["I14"])
    OPERATING_HOURS_CIRCULATION_PUMP = TagData(["I18"])
    OPERATING_HOURS_SOURCE_PUMP = TagData(["I20"])
    OPERATING_HOURS_SOLAR = TagData(["I22"])
    ENABLE_HEATING = TagData(
        ["I30"], read_function=_parse_state, write_function=_write_state, writeable=True
    )  # pylint: disable=line-too-long
    ENABLE_COOLING = TagData(
        ["I31"], read_function=_parse_state, write_function=_write_state, writeable=True
    )  # pylint: disable=line-too-long
    ENABLE_WARMWATER = TagData(
        ["I32"], read_function=_parse_state, write_function=_write_state, writeable=True
    )  # pylint: disable=line-too-long
    ENABLE_POOL = TagData(
        ["I33"], read_function=_parse_state, write_function=_write_state, writeable=True
    )  # pylint: disable=line-too-long
    ENABLE_MIXING1 = TagData(
        ["I37"], read_function=_parse_state, write_function=_write_state, writeable=True
    )  # pylint: disable=line-too-long
    ENABLE_MIXING2 = TagData(
        ["I38"], read_function=_parse_state, write_function=_write_state, writeable=True
    )  # pylint: disable=line-too-long
    ENABLE_MIXING3 = TagData(
        ["I39"], read_function=_parse_state, write_function=_write_state, writeable=True
    )  # pylint: disable=line-too-long
    ENABLE_PV = TagData(
        ["I41"], read_function=_parse_state, write_function=_write_state, writeable=True
    )  # pylint: disable=line-too-long
    STATE_SOURCEPUMP = TagData(["I51"], bit=0)
    STATE_HEATINGPUMP = TagData(["I51"], bit=1)
    STATE_EVD = TagData(["I51"], bit=2)
    STATE_COMPRESSOR = TagData(["I51"], bit=3)
    STATE_COMPRESSOR2 = TagData(["I51"], bit=4)
    STATE_EXTERNAL_HEATER = TagData(["I51"], bit=5)
    STATE_ALARM = TagData(["I51"], bit=6)
    STATE_COOLING = TagData(["I51"], bit=7)
    STATE_WATER = TagData(["I51"], bit=8)
    STATE_POOL = TagData(["I51"], bit=9)
    STATE_SOLAR = TagData(["I51"], bit=10)
    STATE_COOLING4WAY = TagData(["I51"], bit=11)
    ALARM = TagData(["I52"])
    INTERRUPTIONS = TagData(["I53"])
    STATE_SERVICE = TagData(["I135"])
    STATUS_HEATING = TagData(["I137"], read_function=_parse_status)
    STATUS_COOLING = TagData(["I138"], read_function=_parse_status)
    STATUS_WATER = TagData(["I139"], read_function=_parse_status)
    INFO_SERIES = TagData(["I105"], read_function=_parse_series)
    INFO_ID = TagData(["I110"], read_function=_parse_id)
    INFO_SERIAL = TagData(
        ["I114", "I115"],
        writeable=False,
        read_function=_parse_sn,
    )
    ADAPT_HEATING = TagData(["I263"], writeable=True)
    ADAPT_MIXING1 = TagData(["I776"], writeable=True)
    ADAPT_MIXING2 = TagData(["I896"], writeable=True)
    ADAPT_MIXING3 = TagData(["I1017"], writeable=True)
    HEATPUMP_COP_YEAR = TagData(["I1261"],read_function=_parse_cop_year)
    MANUAL_HEATINGPUMP = TagData(["I1270"])
    MANUAL_SOURCEPUMP = TagData(["I1281"])
    MANUAL_SOLARPUMP1 = TagData(["I1287"])
    MANUAL_SOLARPUMP2 = TagData(["I1289"])
    MANUAL_TANKPUMP = TagData(["I1291"])
    MANUAL_VALVE = TagData(["I1293"])
    MANUAL_POOLVALVE = TagData(["I1295"])
    MANUAL_COOLVALVE = TagData(["I1297"])
    MANUAL_4WAYVALVE = TagData(["I1299"])
    MANUAL_MULTIEXT = TagData(["I1319"])

    # SERVICE_HEATING = TagData(["D251"])
    # SERVICE_COOLING = TagData(["D252"])
    # SERVICE_WATER = TagData(["D117"])
    # SERVICE_HEATING_D23 = TagData(["D23"])
    # SERVICE_HEATING_D24 = TagData(["D24"])
    # SERVICE_WATER_D118 = TagData(["D118"])
    # SERVICE_OPMODE = TagData(["I136"])
    # RAW_D430 = TagData(["D430"])  # animation
    # RAW_D28 = TagData(["D28"])  # ?QE
    # RAW_D879 = TagData(["D879"])  # ?RMH
    # MODE_HEATING_PUMP = TagData(["A522"])
    # MODE_HEATING = TagData(["A530"])
    # MODE_HEATING_EXTERNAL = TagData(["A528"])
    # MODE_COOLING = TagData(["A532"])
    # MODE_WATER = TagData(["A534"])
    # MODE_POOL = TagData(["A536"])
    # MODE_SOLAR = TagData(["A538"])

    def __hash__(self) -> int:
        return hash(self.name)


#
# Class to control Waterkotte Ecotouch heatpumps.
#
class Ecotouch:
    """Ecotouch Class"""

    auth_cookies = None


    def __init__(self, host, logger=None):
        global _LOGGER
        _LOGGER = logger or logging.getLogger(__name__)
        #Ecotouch._LOGGER = logger or logging.getLogger(__name__)
        self.hostname = host
        self.username = "waterkotte"
        self.password = "waterkotte"

    # extracts statuscode from response
    def get_status_response(self, r):  # pylint: disable=invalid-name
        """get_status_response"""
        match = re.search(r"^#([A-Z_]+)", r, re.MULTILINE)
        if match is None:
            raise InvalidResponseException(
                "Ungültige Antwort. Konnte Status nicht auslesen."
            )
        return match.group(1)

    # performs a login. Has to be called before any other method.
    async def login(self, username="waterkotte", password="waterkotte"):
        """Login to Heat Pump"""
        args = {"username": username, "password": password}
        self.username = username
        self.password = password
        # r = requests.get("http://%s/cgi/login" % self.hostname, params=args)
        async with aiohttp.ClientSession() as session:
            # r = await session.get("http://%s/cgi/login" % self.hostname, params=args)
            r = await session.get(
                f"http://{self.hostname}/cgi/login", params=args
            )  # pylint: disable=invalid-name
            async with r:
                assert r.status == 200
                # r = await resp.text()

                _LOGGER.debug(f"Login Respone Text{await r.text()} HTTP Code:{r.status}")
                if self.get_status_response(await r.text()) != "S_OK":
                    raise StatusException(
                        f"Fehler beim Login: Status:{self.get_status_response(await r.text())}"
                    )
                self.auth_cookies = r.cookies

    async def logout(self):
        """Logout function"""
        async with aiohttp.ClientSession() as session:
            # r = await session.get("http://%s/cgi/login" % self.hostname, params=args)
            r = await session.get(
                f"http://{self.hostname}/cgi/logout"
            )  # pylint: disable=invalid-name
            async with r:
                # assert r.status == 200
                # r = await resp.text()

                _LOGGER.debug(f"Logout Respone Text{await r.text()} HTTP Code:{r.status}")
                #_LOGGER.debug(r.status)
                # if self.get_status_response(await r.text()) != "S_OK":
                #     raise StatusException(
                #         f"Fehler beim Logout: Status:{self.get_status_response(await r.text())}"
                #     )
                self.auth_cookies = None

    async def read_value(self, tag: EcotouchTag):
        """Read a value from Tag"""
        res = await self.read_values([tag])
        if tag in res:
            return res[tag]
        return None

    async def write_values(self, kv_pairs: Collection[Tuple[EcotouchTag, Any]]):
        """Write values to Tag"""
        to_write = {}
        result = {}
        for k, v in kv_pairs:  # pylint: disable=invalid-name
            if not k.writeable:
                raise InvalidValueException("tried to write to an readonly field")
            k.write_function(k, v, to_write)
            #####
            res = await self._write_tag(to_write.keys(), to_write.values())
            # res = await self._write_tag(k[0][0], to_write[k[0][0]])
            if res is not None and len(res[0]) > 0:
                all_ok = True
                for value in res[1]:
                    if res[1][value] != "S_OK":
                        all_ok = False
                if all_ok:
                    val = k.read_function(k, res[0], k.bit)
                    result[k[0][0]] = {"status": res[1][value], "value": val}
                # if res[k[0][0]]['status'] == "S_OK":
                #     val = k.read_function(k, {k[0][0]: res[k[0][0]]['value']}, k.bit)
                #     result[k[0][0]] = ({'status': res[k[0][0]]['status'], 'value': val})

        # for k, v in to_write.items():  # pylint: disable=invalid-name
        #     res = await self._write_tag(k, v)
        #     if res['status'] == "S_OK":
        #         val= k.read_function(k, v, k.bit)
        #         result.update({'status': res['status'], 'value': val})
        return result

    async def write_value(self, tag, value):
        """Write a value"""
        return await self.write_values([(tag, value)])

    async def read_values(self, tags: Sequence[EcotouchTag]):
        """Async read values"""
        # create flat list of ecotouch tags to be read
        e_tags = list(set([etag for tag in tags for etag in tag.tags]))
        e_values, e_status = await self._read_tags(e_tags)
        _LOGGER.debug(f"read_values: tags: {e_tags}")
        _LOGGER.debug(f"read_values: values: {e_values}")
        result = {}
        # result_status = {}
        for tag in tags:
            # tag2=tag._replace(status=e_status[tag.tags[0]])
            # tag.status[0]=e_status[tag.tags[0]]
            # if len(tag.status)==0:
            #     tag.status.append(e_status[tag.tags[0]])
            # else:
            #     tag.status.clear()
            #     tag.status.append(e_status[tag.tags[0]] + str(random.randint(1,10)))
            # result_status[tag] = e_status[tag.tags[0]] + str(random.randint(1,10))
            # tag.status=e_status[tag.tags[0]]
            # e_inactive = False
            for tag_status in tag.tags:
                try:
                    if e_status[tag_status] == "E_INACTIVE":
                        if e_values[tag.tags[0]] is not None:
                            val = e_values[tag.tags[0]]
                        else:
                            val = None
                    else:
                        val = tag.read_function(tag, e_values, tag.bit)
                except KeyError:
                    val = None
            #         e_inactive = True
            # if e_inactive is False:
            #     val = tag.read_function(tag, e_values, tag.bit)
            # else:
            #     val = None
            try:
                result[tag] = {
                    "value": val,
                    "status": e_status[tag_status],
                }  # pylint: disable=undefined-loop-variable
            except KeyError:
                print(
                    f"Key Error in read_values. tagstatus:{tag_status} tag: {tag} val: {val} e_status:{e_status} e_values:{e_values} reguested tags:{tags}"
                )
        return result

    #
    # reads a list of ecotouch tags
    #
    async def _read_tags(
        # self, tags: Sequence[EcotouchTag], results={}, results_status={}
        self,
        tags: Sequence[EcotouchTag],
        results=None,
        results_status=None,
    ):
        """async read tags"""
        if results is None:
            results = {}
        if results_status is None:
            results_status = {}

        while len(tags) > MAX_NO_TAGS:
            results, results_status = await self._read_tags(
                tags[:MAX_NO_TAGS], results, results_status
            )
            tags = tags[MAX_NO_TAGS:]
        # if len(tags) > 0:
        #     results, results_status = await self._read_tags(
        #         tags, results, results_status)

        args = {}
        args["n"] = len(tags)
        for i in range(len(tags)):
            args[f"t{(i + 1)}"] = tags[i]
        # r = requests.get(
        #     "http://%s/cgi/readTags" % self.hostname,
        #     params=args,
        #     cookies=self.auth_cookies,
        # )
        async with aiohttp.ClientSession(cookies=self.auth_cookies) as session:

            async with session.get(
                f"http://{self.hostname}/cgi/readTags", params=args
            ) as resp:
                _LOGGER.debug("_read_tags: request: %s",resp.request_info)
                r = await resp.text()  # pylint: disable=invalid-name
                # print(r)
                if r == "#E_NEED_LOGIN\n":
                    await self.login(self.username, self.password)
                    return results, results_status
                _LOGGER.debug("_read_tags: response: %s",r)
                for tag in tags:
                    match = re.search(
                        f"#{tag}\t(?P<status>[A-Z_]+)\n\d+\t(?P<value>\-?\d+)",  # pylint: disable=anomalous-backslash-in-string
                        r,
                        re.MULTILINE,
                    )
                    if match is None:
                        match = re.search(
                            # r"#%s\tE_INACTIVETAG" % tag,
                            f"#{tag}\tE_INACTIVETAG",
                            r,
                            re.MULTILINE,
                        )
                        # val_status = "E_INACTIVE"  # pylint: disable=possibly-unused-variable
                        # print("Tag: %s is inactive!", tag)
                        if match is None:
                            raise Exception(tag + " tag not found in response")

                        results_status[tag] = "E_INACTIVE"
                        results[tag] = None
                    else:
                        results_status[tag] = match.group("status")
                        results[tag] = match.group("value")

        return results, results_status

    #
    # writes <value> into the tag <tag>
    #
    async def _write_tag(self, tags: List[str], value: List[Any]):
        """write tag"""
        args = {}
        args["n"] = len(tags)
        args["returnValue"] = "true"
        args["rnd"] = str(datetime.timestamp(datetime.now()))
        # for i in range(len(tags)):
        #    args[f"t{(i + 1)}"] = tags[i]
        # for i in range(len(tag.tags)):
        #     et_values[tag.tags[i]] = vals[i]
        # print(et_values)
        for i, tag in enumerate(tags):
            args[f"t{i+1}"] = tag
            args[f"v{i+1}"] = list(value)[i]

        # args = {
        #     "n": 1,
        #     "returnValue": "true",
        #     "t1": tag,
        #     "v1": value,
        #     'rnd': str(datetime.timestamp(datetime.now()))
        # }
        # result = {}
        results = {}
        results_status = {}
        async with aiohttp.ClientSession(cookies=self.auth_cookies) as session:

            async with session.get(
                f"http://{self.hostname}/cgi/writeTags", params=args
            ) as resp:
                r = await resp.text()  # pylint: disable=invalid-name
                # print(r)
                if r == "#E_NEED_LOGIN\n":
                    await self.login(
                        self.username, self.password
                    )  # pylint: disable=possibly-unused-variable
                    res = await self._write_tag(tags, value)
                    return res
                ###
                for tag in tags:
                    match = re.search(
                        f"#{tag}\t(?P<status>[A-Z_]+)\n\d+\t(?P<value>\-?\d+)",  # pylint: disable=anomalous-backslash-in-string
                        r,
                        re.MULTILINE,
                    )
                    if match is None:
                        match = re.search(
                            # r"#%s\tE_INACTIVETAG" % tag,
                            f"#{tag}\tE_INACTIVETAG",
                            r,
                            re.MULTILINE,
                        )
                        # val_status = "E_INACTIVE"  # pylint: disable=possibly-unused-variable
                        # print("Tag: %s is inactive!", tag)
                        if match is None:
                            raise Exception(tag + " tag not found in response")

                        # if val_status == "E_INACTIVE":
                        results_status[tag] = "E_INACTIVE"
                        results[tag] = None
                    else:
                        results_status[tag] = "S_OK"
                        results[tag] = match.group("value")
            _LOGGER.debug(f"results: {results}")
            _LOGGER.debug(f"results_status: {results_status}")
            return results, results_status