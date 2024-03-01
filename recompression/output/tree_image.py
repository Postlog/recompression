import anytree
import anytree.exporter as exporter

from recompression.models import compression_node as cn
from utils.time import timeit


class TreeImage:
    @timeit("tree image generation")
    def generate(self, path: str, root: cn.CompressionNode):
        anytree_root = self._convert_to_anytree_node(root)

        exporter.DotExporter(anytree_root, nodeattrfunc=self._node_attr_func).to_picture(path)

    def _node_attr_func(self, node: anytree.Node) -> str | None:
        if hasattr(node, 'is_solution'):
            return 'color=green'
        elif hasattr(node, 'is_bad'):
            return 'color=red'

        return None

    def _convert_to_anytree_node(self, node: cn.CompressionNode):
        name = f'{node.option}\n' if node.option is not None and (node.option.restriction is not None or len(
            node.option.substitutions) != 0) else ''
        name += f'{node.compression_action[0]} -> {node.compression_action[1]}\n' if node.compression_action is not None else ''

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
