import log


class Deploy:

    def __init__(self, core, lastname=None):
        self.firstname = type(self).__name__
        self.lastname = lastname
        self.name = self.firstname if lastname is None else self.firstname + ":" + lastname
        self.core = core
        self.nodes = {}
    
    def add_node(self, node):
        if node.name in self.nodes:
            log.warn("Reusing name when adding a node. Removing previous node")
            self.remove_node(node.name)
        
        self.nodes[node.name] = node
    
    def remove_node(self, node_name):
        if node_name in self.nodes:
            node = self.nodes[node_name]
            del self.nodes[node_name]
            node.on_remove()

    def on_remove(self):
        for node in self.nodes:
            node.on_remove()

    def require_device(self, device_name):
        self.core.require_device(device_name)
