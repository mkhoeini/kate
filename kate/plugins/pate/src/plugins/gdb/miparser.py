#
# Copyright (C) 2012 Shaheed Haque <srhaque@theiet.org>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) version 3.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with this library; see the file COPYING.LIB.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

from ply import lex, yacc
from PyKDE4.kdecore import KStandardDirs

class MiParser():
    """Parse output generated by GDB's MI."""
    def __init__(self):
        self.lexer = lex.lex(module = self)
        #
        # To enable generation of parser.out, debug = 1
        #
        self.parser = yacc.yacc(module = self, debug = 0, \
                tabmodule = __name__ + "generated", \
                outputdir = str(KStandardDirs().saveLocation("tmp")))

    def testLexer(self, data):
        """Test it output."""
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok: break
            print tok

    def parse(self, input):
        return self.parser.parse(input, lexer = self.lexer)

    #########
    # LEXER #
    #########
    tokens = (
        'NAME',
        'QUOTEDVALUE',
        'EQUALS',
        'LBRACE',
        'RBRACE',
        'LBRACKET',
        'RBRACKET',
        'COMMA',
    )

    # Regular expression rules for simple tokens
    t_NAME     = r'[a-zA-Z\d_\-]+'
    t_EQUALS   = r'='
    t_LBRACE   = r'{'
    t_RBRACE   = r'}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_COMMA    = r','

    def t_QUOTEDVALUE(self, t):
        r'"(\\"|[^"])*"'
        t.value = t.value[1:-1]
        #
        # Convert decimal and hex integers to the most compact form we can.
        #
        try:
            t.value = str(int(t.value))
        except ValueError:
            try:
                t.value = hex(int(t.value, 16))
            except ValueError:
                pass
        return t

    # Error handling rule
    def t_error(self, t):
        print "Illegal character '{}' at offset {} in '{}'".format(t.value[0], t.lexpos, t.lexer.lexdata[:t.lexpos + 1])
        t.lexer.skip(1)

    ##########
    # PARSER #
    ##########
    def p_named_values_empty(self, p):
        'named_values : '
        p[0] = dict()
        #print "p_named_values_empty", p[0]

    def p_named_values_one(self, p):
        'named_values : named_value'
        p[0] = dict(p[1])
        #print "p_named_values_one", p[0]

    def p_named_values_multiple1(self, p):
        'named_values : named_values COMMA named_value'
        p[0] = p[1]
        p[0].update(p[3])
        #print "p_named_values_multiple1", p[0]

    def p_named_values_multiple2(self, p):
        #
        # This is here to handle arrays without [] in support of testBreakInsert
        # for overloaded symbols. TODO: handle it as a sntax error recovery
        # case.
        #
        'named_values : named_values COMMA value'
        p[0] = dict()
        for k, v in p[1].iteritems():
            if isinstance(v, dict):
                v = [v]
            v.append(p[3])
            p[0][k] = v
        #print "p_named_values_multiple2", p[0]

    def p_named_value(self, p):
        'named_value : NAME EQUALS value'
        p[0] = {p[1]: p[3]}
        #print "p_named_value", p[0]

    def p_value_simple(self, p):
        'value : QUOTEDVALUE'
        p[0] = p[1]
        #print "p_value_simple", p[0]

    def p_value_nested1(self, p):
        'value : LBRACE named_values RBRACE'
        p[0] = p[2]
        #print "p_value_nested1", p[0]

    def p_value_nested2(self, p):
        'value : LBRACKET array_values RBRACKET'
        p[0] = p[2]
        #print "p_value_nested2", p[0]

    def p_array_empty(self, p):
        'array_values : '
        p[0] = []
        #print "p_array_empty", p[0]

    def p_array_one1(self, p):
        'array_values : value'
        p[0] = [p[1]]
        #print "p_array_one1", p[0]

    def p_array_one2(self, p):
        'array_values : named_value'
        p[0] = [p[1]]
        #print "p_array_one2", p[0]

    def p_array_multiple1(self, p):
        'array_values : value COMMA array_values'
        p[0] = [p[1]]
        p[0].extend(p[3])
        #print "p_array_multiple1", p[0]

    def p_array_multiple2(self, p):
        'array_values : named_value COMMA array_values'
        p[0] = [p[1]]
        p[0].extend(p[3])
        #print "p_array_multiple2", p[0]

    def p_error(self, p):
        print "Syntax error near offset {} in '{}'".format(p.lexpos, p.lexer.lexdata[:p.lexpos + 1])


if __name__ == "__main__":
    testBreakList='BreakpointTable={nr_rows="2",nr_cols="6",hdr=[{width="7",alignment="-1",col_name="number",colhdr="Num"},{width="14",alignment="-1",col_name="type",colhdr="Type"},{width="4",alignment="-1",col_name="disp",colhdr="Disp"},{width="3",alignment="-1",col_name="enabled",colhdr="Enb"},{width="18",alignment="-1",col_name="addr",colhdr="Address"},{width="40",alignment="2",col_name="what",colhdr="What"}],body=[bkpt={number="1",type="breakpoint",disp="keep",enabled="y",addr="0x0000000000400680",func="main(int, char**)",file="/home/.../kate_dummy.cpp",fullname="/home/.../kate_dummy.cpp",line="3",times="0",original-location="main"},bkpt={number="2",type="breakpoint",disp="keep",enabled="y",addr="0x0000000000400680",func="main(int, char**)",file="/home/.../kate_dummy.cpp",fullname="/home/.../kate_dummy.cpp",line="3",times="0",original-location="main"}]}'
    testBreakInsert='bkpt={number="2",type="breakpoint",disp="keep",enabled="y",addr="<MULTIPLE>",times="0",original-location="QWidget::QWidget"},{number="2.1",enabled="y",addr="0x00007ffff6d601b0",at="<QWidget::QWidget(QWidgetPrivate&, QWidget*, QFlags<Qt::WindowType>)>"},{number="2.2",enabled="y",addr="0x00007ffff6d60270",at="<QWidget::QWidget(QWidget*, char const*, QFlags<Qt::WindowType>)>"},{number="2.3",enabled="y",addr="0x00007ffff6d603c0",at="<QWidget::QWidget(QWidget*, QFlags<Qt::WindowType>)>"}'
    testThreads='threads=[{id="1",target-id="Thread 0x7ffff7fe1780 (LWP 5376)",name="kate",frame={level="0",addr="0x0000000000400680",func="main",args=[{name="argc",value="1"},{name="argv",value="0x7fffffffdd88"}],file="/home/.../kate_dummy.cpp",fullname="/home/.../kate_dummy.cpp",line="3"},state="stopped",core="1"}],current-thread-id="1"'
    testFrame='frame={level="3",addr="0x00007ffff6d90198",func="QClipboard::QClipboard(QObject*)",from="/usr/lib/x86_64-linux-gnu/libQtGui.so.4"}'
    testLocals='variables=[{name="kateVersion",value="\\"3.9.2\\" = {[0] = 51 \'3\', [1] = 46 \'.\', [2] = 57 \'9\', [3] = 46 \'.\', [4] = 50 \'2\'}"},{name="serviceName",value="\\"\\""},{name="start_session_set",value="<optimised out>"},{name="start_session",value="\\"\\""},{name="app",value="{<KApplication> = {<No data fields>}, static staticMetaObject = {d = {superdata = 0x7ffff63e81e0 <KApplication::staticMetaObject>, stringdata = 0x7ffff6469d00 <qt_meta_stringdata_KateApp> \\"KateApp\\", data = 0x7ffff6469d60 <qt_meta_data_KateApp>, extradata = 0x7ffff667cce0 <KateApp::staticMetaObjectExtraData>}}, static staticMetaObjectExtraData = {objects = 0x0, static_metacall = 0x7ffff6433810 <KateApp::qt_static_metacall(QObject*, QMetaObject::Call, int, void**)>}, m_shouldExit = false, m_args = 0x7ffff7bcfd28, m_application = 0x1, m_docManager = 0x20a240, m_pluginManager = 0x0, m_sessionManager = 0x0, m_adaptor = 0x400688 <_start>, m_mainWindows = QList<KateMainWindow *> = {[0] = 0x0, [1] = 0x0, [2] = 0x0, [3] = 0x0, [4] = 0x0, [5] = 0x0, [6] = 0x0, [7] = 0x0, [8] = 0x0, [9] = 0x0, [10] = 0x0, [11] = 0x0, [12] = 0x0, [13] = 0x0, [14] = 0x0, [15] = 0x0, [16] = 0x0, [17] = 0x0, [18] = 0x0, [19] = 0x0, [20] = 0x0, [21] = 0x0, [22] = 0x0, [23] = 0x0, [24] = 0x0, [25] = 0x0, [26] = 0x0, [27] = 0x0, [28] = 0x0, [29] = 0x0, [30] = 0x0, [31] = 0x0, [32] = 0x0, [33] = 0x0, [34] = 0x0, [35] = 0x0, [36] = 0x0, [37] = 0x0, [38] = 0x0, [39] = 0x0, [40] = 0x0, [41] = 0x0, [42] = 0x0, [43] = 0x0, [44] = 0x0, [45] = 0x0, [46] = 0x0, [47] = 0x0, [48] = 0x0, [49] = 0x0, [50] = 0x0, [51] = 0x0, [52] = 0x0, [53] = 0x0, [54] = 0x0, [55] = 0x0, [56] = 0x0, [57] = 0x0, [58] = 0x0, [59] = 0x0, [60] = 0x0, [61] = 0x0, [62] = 0x0, [63] = 0x0, [64] = 0x0, [65] = 0x0, [66] = 0x0, [67] = 0x0, [68] = 0x0, [69] = 0x0, [70] = 0x0, [71] = 0x0, [72] = 0x0, [73] = 0x0, [74] = 0x0, [75] = 0x0, [76] = 0x0, [77] = 0x0, [78] = 0x0, [79] = 0x0, [80] = 0x0, [81] = 0x0, [82] = 0x0, [83] = 0x0, [84] = 0x0, [85] = 0x0, [86] = 0x0, [87] = 0x0, [88] = 0x0, [89] = 0x0, [90] = 0x0, [91] = 0x0, [92] = 0x0, [93] = 0x0, [94] = 0x0, [95] = 0x0, [96] = 0x0, [97] = 0x0, [98] = 0x0, [99] = 0x0, [100] = 0x0, [101] = 0x0, [102] = 0x0, [103] = 0x0, [104] = 0x0, [105] = 0x0, [106] = 0x0, [107] = 0x0, [108] = 0x0, [109] = 0x0, [110] = 0x0, [111] = 0x0, [112] = 0x0, [113] = 0x0, [114] = 0x0, [115] = 0x0, [116] = 0x0, [117] = 0x0, [118] = 0x0, [119] = 0x0, [120] = 0x0, [121] = 0x0, [122] = 0x0, [123] = 0x0, [124] = 0x0, [125] = 0x0, [126] = 0x0, [127] = 0x0, [128] = 0x0, [129] = 0x0, [130] = 0x0, [131] = 0x0, [132] = 0x0, [133] = 0x0, [134] = 0x0, [135] = 0x0, [136] = 0x0, [137] = 0x0, [138] = 0x0, [139] = 0x0, [140] = 0x0, [141] = 0x0, [142] = 0x0, [143] = 0x0, [144] = 0x0, [145] = 0x0, [146] = 0x0, [147] = 0x0, [148] = 0x0, [149] = 0x0, [150] = 0x0, [151] = 0x0, [152] = 0x0, [153] = 0x0, [154] = 0x0, [155] = 0x0, [156] = 0x0, [157] = 0x0, [158] = 0x0, [159] = 0x0, [160] = 0x0, [161] = 0x0, [162] = 0x0, [163] = 0x0, [164] = 0x0, [165] = 0x0, [166] = 0x0, [167] = 0x0, [168] = 0x0, [169] = 0x0, [170] = 0x0, [171] = 0x0, [172] = 0x0, [173] = 0x0, [174] = 0x0, [175] = 0x0, [176] = 0x0, [177] = 0x0, [178] = 0x0, [179] = 0x0, [180] = 0x0, [181] = 0x0, [182] = 0x0, [183] = 0x0, [184] = 0x0, [185] = 0x0, [186] = 0x0, [187] = 0x0, [188] = 0x0, [189] = 0x0, [190] = 0x0, [191] = 0x0, [192] = 0x0, [193] = 0x0, [194] = 0x0, [195] = 0x0, [196] = 0x0, [197] = 0x0, [198] = 0x0, [199] = 0x0...}, m_mainWindowsInterfaces = QList<Kate::MainWindow *> = {[0] = <error reading variable>"},{name="aboutData",value="{d = 0x60a880}"},{name="options",value="{d = 0x622320}"},{name="args",value="<optimised out>"},{name="i",value="0x624740"},{name="mapSessionRii",value="empty QMap<QString, KateRunningInstanceInfo *>"},{name="kateServices",value="QStringList<QString> = {[0] = \\"org.kde.kate-2632\\"}"},{name="force_new",value="<optimised out>"},{name="session_already_opened",value="<optimised out>"},{name="foundRunningService",value="<optimised out>"},{name="argc",arg="1",value="<optimised out>"},{name="argv",arg="1",value="0x7fffffffdd00"}]'
    testArgs='stack-args=[frame={level="0",args=[]},frame={level="1",args=[]},frame={level="2",args=[]},frame={level="3",args=[]},frame={level="4",args=[]},frame={level="5",args=[]},frame={level="6",args=[]},frame={level="7",args=[{name="this",value="0x7fffffffdc10"},{name="args",value="0x6237f0"}]},frame={level="8",args=[{name="argc",value="<optimised out>"},{name="argv",value="0x7fffffffdd00"}]},frame={level="9",args=[]},frame={level="10",args=[]}]'
    testRegisterList='register-names=["eax","ecx","edx","ebx","esp","ebp","esi","edi","eip","eflags","cs","ss","ds","es","fs","gs","st0","st1","st2","st3","st4","st5","st6","st7","fctrl","fstat","ftag","fiseg","fioff","foseg","fooff","fop","xmm0","xmm1","xmm2","xmm3","xmm4","xmm5","xmm6","xmm7","mxcsr","","","","","","","","","orig_eax","al","cl","dl","bl","ah","ch","dh","bh","ax","cx","dx","bx","","bp","si","di","mm0","mm1","mm2","mm3","mm4","mm5","mm6","mm7"]'
    parser = MiParser()
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(parser.parse(testBreakList))
    pp.pprint(parser.parse(testThreads))
    pp.pprint(parser.parse(testFrame))
    pp.pprint(parser.parse(testLocals))
    pp.pprint(parser.parse(testArgs))
    pp.pprint(parser.parse(testRegisterList))
    pp.pprint(parser.parse(testBreakInsert))
    #parser.testLexer(testRegisterList)
    #results = parser.parse(testRegisterList)
    #print results
    #u = results[0][1]
    #print u
    #for i in u:
        #print i["name"] + "=" + i["value"]
