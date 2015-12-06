from . import ast
from . import definitions
from . import utils


class Symbol(object):

    def __init__(self, node = None):
        self.entries = dict()
        self.node = node

    def __iter__(self):
        return self.entries.iterkeys()

    def __contains__(self, key):
        return key in self.entries

    def __getitem__(self, key):
        return self.entries[key]

    def append(self, name, node):
        if name in self.entries:
            assert(0)
        self.entries[name] = node


def mapSymbols(rootNode, rootSmTable):
    smTables = list()
    scopeSelectors = list()

    def enterScope(sym):
        smTables.insert(0, sym)

    def leaveScope():
        smTables.pop(0)

    def register(node):
        sym = Symbol(node)
        smTables[0].append(node.name, sym)
        return sym

    def seekSymbol(name):
        # if len(selectedScope):
        #     if name in selectedScope[0]:
        #         return selectedScope[0][name]
        if len(scopeSelectors) and len(scopeSelectors[0]):
            if name in scopeSelectors[0][0]:
                return scopeSelectors[0][0][name]
        else:
            for x in smTables:
                if name in x:
                    return x[name]
        return False

    def mapIdentifier(identifier):
        symbol = seekSymbol(identifier.value)
        if not symbol:
            raise definitions.SemanticError(identifier, "referenced underclared symbol '%s'" % identifier.value)
        identifier._symbol = symbol
        return symbol

    def visitorDefMapper(walker, node):
        if not isinstance(node, ast.File):
            if isinstance(node, ast.SymbolDefinition):
                sym = register(node)
            # if isinstance(node, ast.Container):
                enterScope(sym)
                walker.walk()
                leaveScope()
        walker.walk()

    def visitorRefMapper(walker, node):
        if not isinstance(node, ast.File):
            # if isinstance(node, ast.Container):
            if isinstance(node, ast.SymbolDefinition):
                enterScope(smTables[0][node.name])
                walker.walk()
                leaveScope()
            elif isinstance(node, ast.SelectionOp):
                # print(node.lvalue)
                selectionEntered = False
                if not isinstance(node.getParent(), ast.SelectionOp):
                    scopeSelectors.insert(0, list())
                    selectionEntered = True
                walker.walk()
                if selectionEntered:
                    scopeSelectors.pop(0)
                # awaitingSelectorSym.insert(0, True)
                # walker.walk(node.lvalue)
                # sym = awaitingSelectorSym.pop(0)
                # if isinstance(sym.node.type, ast.UserType):
                #     selectedScope.insert(0, sym.node.type.identifier._symbol)
                #     walker.walk(node.rvalue)
                #     selectedScope.pop(0)
                # else:
                #     # TODO ??
                #     walker.walk(node.rvalue)
                # sym = mapIdentifier(node.lvalue)
                # if isinstance(sym.node.type, ast.UserType):
                #     selectedScope.insert(0, sym.node.type.identifier._symbol)
                #     walker.walk()
                #     selectedScope.pop(0)
                # else:
                #     walker.walk()
            elif isinstance(node, ast.Identifier):
                # if not node._symbol:
                #     mapIdentifier(node)
                sym = mapIdentifier(node)
                # if len(awaitingSelectorSym):
                #     awaitingSelectorSym[0] = sym
                walker.walk()
            else:
                walker.walk()

            #
            if isinstance(node.getParent(), ast.SelectionOp) and not isinstance(node, ast.SelectionOp):
                if isinstance(node, ast.Identifier):
                    sym = node._symbol
                elif isinstance(node, ast.ArraySubscript):
                    sym = node.value._symbol
                else:
                    assert(0)
                if isinstance(sym.node.type, ast.UserType):
                    sym = sym.node.type.identifier._symbol
                    scopeSelectors[0].insert(0, sym)
        else:
            walker.walk()

    smTables.append(rootSmTable)
    utils.NodeWalker(rootNode, visitorDefMapper)
    utils.NodeWalker(rootNode, visitorRefMapper)
