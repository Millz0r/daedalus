'''
valuation - Portfolio valuation module corresponding to M11 on our architecture chart. This module takes all of the data that describes a
portfolio, analyzes it and provides an offer matrix. The offer matrix is a sensativity analysis of possible counter-offers with key
ratios and profit computed for each possible counter-offer.
'''
import daedalus.config
import daedalus.queueing.mixins

from daedalus.queueing import queue_manager
from daedalus.valuation.valuation import valuate

__all__ = ['valuate']
