"""Remove migrated rows from authored INSERTs without losing neighboring rules.

This source-editing helper uses CSC's SQL lexer; it never executes SQL or edits
an installed mod. Only explicit VALUES tuples or a wholly selected SELECT are
removed. Comments survive so mixed Service/material/fixed blocks remain readable.
Unrecognized statement shapes fail rather than guessing how to rewrite them.
"""
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'quarter_contracts'))
from format_sql_layout import LEXER


def remove_rows(source, table, column, selected):
    tokens=[m for m in LEXER.finditer(source)if m.lastgroup not in('space','comment')]
    edits=[];removed=0;start=0
    for end,t in enumerate(tokens):
        if t.group()!=';':continue
        statement=tokens[start:end+1];start=end+1
        if not statement or statement[0].group().upper()!='INSERT':continue
        words=[x.group().upper()if x.lastgroup=='word'else x.group()for x in statement]
        at=words.index('INTO')if 'INTO'in words else -1
        if at<0 or words[at+1]!=table.upper():continue
        assert words[at+2]=='(',table
        close=words.index(')',at+3)
        columns=[x.group().strip('"')for x in statement[at+3:close]if x.group()!=',']
        field=columns.index(column)
        shape=words[close+1]
        if shape=='SELECT':
            # Inspect the selected column expression, not literals elsewhere in
            # FROM/WHERE or another output column. A dynamic CASE could mix
            # migrated and retained rows; require an explicit rewrite for that.
            outputs=[];depth=0;first=close+2
            if words[first]=='DISTINCT':first+=1
            for i in range(first,len(statement)):
                value=words[i]
                if depth==0 and value in('FROM','WHERE',';'):
                    outputs.append(statement[first:i]);break
                if value=='(':depth+=1
                elif value==')':depth-=1
                elif value==','and depth==0:outputs.append(statement[first:i]);first=i+1
            assert len(outputs)==len(columns),(table,'SELECT output shape')
            expression=outputs[field]
            values={x.group()[1:-1].replace("''", "'")for x in expression if x.group().startswith("'")}
            selected_output=values & selected
            if selected_output:
                assert len(expression)==1,(table,'mixed/dynamic SELECT output requires explicit migration')
                body=source[statement[0].start():statement[-1].end()]
                comments=[m.group()for m in LEXER.finditer(body)if m.lastgroup=='comment']
                edits.append((statement[0].start(),statement[-1].end(),'\n'.join(comments)))
                removed+=1
            continue
        assert shape=='VALUES',(table,shape)
        rows=[];commas=[];depth=0;opened=None;fields=[];first=None
        for i in range(close+2,len(statement)-1):
            token=statement[i];value=token.group()
            if value=='(':
                if depth==0:opened=i;fields=[];first=i+1
                depth+=1
            elif value==')':
                depth-=1
                if depth==0:
                    fields.append(statement[first:i]);rows.append((opened,i,fields))
            elif value==','and depth==1:
                fields.append(statement[first:i]);first=i+1
            elif value==','and depth==0:commas.append(i)
        assert len(commas)==len(rows)-1 and depth==0,(table,'tuple layout')
        deleted=[]
        for j,(a,b,fields)in enumerate(rows):
            assert len(fields)==len(columns),(table,'column count')
            literal=fields[field]
            if len(literal)==1 and literal[0].group().startswith("'"):
                key=literal[0].group()[1:-1].replace("''", "'")
                if key in selected:deleted.append(j)
        if not deleted:continue
        removed+=len(deleted)
        if len(deleted)==len(rows):
            body=source[statement[0].start():statement[-1].end()]
            comments=[m.group()for m in LEXER.finditer(body)if m.lastgroup=='comment']
            edits.append((statement[0].start(),statement[-1].end(),'\n'.join(comments)))
            continue
        retained=[j for j in range(len(rows))if j not in deleted]
        for j in deleted:
            a,b,_=rows[j]
            body=source[statement[a].start():statement[b].end()]
            comments=[m.group()for m in LEXER.finditer(body)if m.lastgroup=='comment']
            edits.append((statement[a].start(),statement[b].end(),'\n'.join(comments)))
        for j,i in enumerate(commas):
            if j not in retained[:-1]:edits.append((statement[i].start(),statement[i].end(),''))
    for a,b,new in sorted(edits,reverse=True):source=source[:a]+new+source[b:]
    return source,removed
