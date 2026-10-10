r"""
Automated SPMD Tensor Sharding Engine for TPU Pods.
Partitions global multidimensional tensors across 2D mesh axes ('data', 'model'),
computing local shard geometries and SPMD partition specifications.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np


@dataclass(frozen=True)
class PartitionSpec:
    """SPMD partition specification mapping tensor dimensions to mesh axes."""
    dim_partitions: Tuple[Optional[str], ...]  # e.g. ('data', None, 'model')


@dataclass(frozen=True)
class ShardGeometry:
    """Local shard geometry for a single TPU chip."""
    chip_id: int
    global_shape: Tuple[int, ...]
    local_shape: Tuple[int, ...]
    slice_ranges: Tuple[Tuple[int, int], ...]
    is_valid_partition: bool


class SPMDShardingOrchestrator:
    r"""
    Manages automated SPMD tensor sharding over a 2D TPU mesh:
    mesh_axes = {'data': dim_x, 'model': dim_y}.
    """

    def __init__(
        self,
        mesh_shape: Tuple[int, int] = (16, 16),
        axis_names: Tuple[str, str] = ("data", "model"),
    ):
        self.mesh_shape = mesh_shape
        self.axis_names = axis_names
        self.axis_sizes = {axis_names[0]: mesh_shape[0], axis_names[1]: mesh_shape[1]}
        self.total_chips = mesh_shape[0] * mesh_shape[1]

    def compute_shard_geometry(
        self,
        global_shape: Tuple[int, ...],
        partition_spec: PartitionSpec,
        chip_id: int,
    ) -> ShardGeometry:
        """Computes local shard shape and slicing coordinates for a given chip."""
        if chip_id < 0 or chip_id >= self.total_chips:
            raise ValueError(f"Invalid chip ID {chip_id} for mesh size {self.total_chips}")

        mesh_x = chip_id % self.mesh_shape[0]
        mesh_y = chip_id // self.mesh_shape[0]
        coord_map = {self.axis_names[0]: mesh_x, self.axis_names[1]: mesh_y}

        local_dims = []
        slices = []

        for dim_idx, axis_name in enumerate(partition_spec.dim_partitions):
            g_len = global_shape[dim_idx]
            if axis_name is None:
                # Replicated across mesh
                local_dims.append(g_len)
                slices.append((0, g_len))
            else:
                axis_size = self.axis_sizes[axis_name]
                if g_len % axis_size != 0:
                    raise ValueError(
                        f"Dimension {dim_idx} of length {g_len} not divisible by axis {axis_name} size {axis_size}"
                    )
                chunk = g_len // axis_size
                coord = coord_map[axis_name]
                start = coord * chunk
                end = start + chunk
                local_dims.append(chunk)
                slices.append((start, end))

        return ShardGeometry(
            chip_id=chip_id,
            global_shape=global_shape,
            local_shape=tuple(local_dims),
            slice_ranges=tuple(slices),
            is_valid_partition=True,
        )

    def shard_tensor(
        self,
        global_tensor: np.ndarray,
        partition_spec: PartitionSpec,
    ) -> List[np.ndarray]:
        """Splits global NumPy tensor into list of local shards for each chip."""
        shards = []
        for chip_id in range(self.total_chips):
            geom = self.compute_shard_geometry(global_tensor.shape, partition_spec, chip_id)
            idx = tuple(slice(s[0], s[1]) for s in geom.slice_ranges)
            shards.append(global_tensor[idx].copy())
        return shards
