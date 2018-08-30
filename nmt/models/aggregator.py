import torch.nn as nn
from .pooling import *


class Aggregator(nn.Module):
    def __init__(self, input_channls, force_output_channels=None, params={}):
        nn.Module.__init__(self)
        mode = params.get("mode", "max")
        self.output_channels = input_channls
        if mode == 'mean':
            self.project = average_code
        elif mode == 'max':
            self.project = max_code
        elif mode == 'truncated-max':
            self.project = truncated_max
        elif mode == 'truncated-mean':
            self.project = truncated_mean
        elif mode == "max-attention":
            self.project = MaxAttention(params, input_channls)
            self.output_channels *= (2 - (params['first_aggregator'] == "skip"))
        elif mode == "max-attention2":
            self.project = MaxAttention2(params, input_channls)
            self.output_channels *= (2 - (params['first_aggregator'] == "skip"))
        else:
            raise ValueError('Unknown mode %s' % mode)
        self.add_lin = 0
        if force_output_channels is not None:
            self.add_lin = 1
            # project with a simple linear layer to the requested dimension
            self.lin = nn.Linear(self.output_channels, force_output_channels)
            self.output_channels = force_output_channels

    def forward(self, tensor, src_lengths, track=False, *args):
        if not track:
            proj = self.project(tensor, src_lengths, track, *args)
            proj = proj.permute(0, 2, 1)
            if self.add_lin:
                return self.lin(proj)
            else:
                return proj
        else:
            # return the squashed vector repr and the pseudo-attention weights:
            proj, attn = self.project(tensor, src_lengths, track, *args)
            proj = proj.permute(0, 2, 1)
            if self.add_lin:
                proj = self.lin(proj)
            return proj, attn




