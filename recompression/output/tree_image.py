import anytree
import anytree.exporter as exporter

from recompression.models import compression_node as cn, option as opt, actions as ac, const as c
from utils.time import timeit


class TreeImage:
    def generate(self, path: str, root: cn.CompressionNode):
        anytree_root = self._convert_to_anytree_node(root)

        exporter.DotExporter(
            anytree_root,
            graph='strict digraph',
            nodeattrfunc=self._node_attr_func,
        ).to_picture(path)

    def _node_attr_func(self, node: anytree.Node) -> str | None:
        if hasattr(node, 'is_solution'):
            return 'color=lightgreen fillcolor=lightgreen style=filled shape=box'
        elif hasattr(node, 'is_bad'):
            return 'color=red shape=box'

        return 'shape=box'

    def _convert_to_anytree_node(self, node: cn.CompressionNode):
        name = f'ID: {node.id}\n'
        name += _get_compression_action_representation(node.compression_action)
        name += _get_option_representation(node.option)
        name += f'{node.equation}'

        attrs = {}
        if node.equation.is_solved:
            attrs["is_solution"] = True
        elif len(node.children) == 0:
            attrs["is_bad"] = True

        anytree_node = anytree.Node(name, **attrs)

        for child in node.children:
            anytree_child = self._convert_to_anytree_node(child)
            anytree_child.parent = anytree_node
        return anytree_node


def _get_option_representation(o: opt.Option | None) -> str:
    subts = 'No substitutions'
    if o is not None and len(o.substitutions) > 0:
        subts = ', '.join([str(s) for s in sorted(o.substitutions, key=lambda x: ord(x.var.sym))])

    restr = 'No restrictions'
    if o is not None and o.restriction is not None:
        restr = str(o.restriction)

    return f'{subts}\n{restr}\n'


def _get_compression_action_representation(
        action: tuple[ac.CompressBlockAction | ac.CompressPairAction, c.BlockConst | c.PairConst] | None,
) -> str:
    return f'{action[0]} → {action[1]}\n' if action is not None else 'No compression action\n'
