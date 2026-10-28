import React from 'react'

const KEYWORDS = new Set([
  'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue',
  'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in',
  'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield',
])
const BUILTINS = new Set([
  'print', 'input', 'len', 'range', 'int', 'float', 'str', 'bool', 'list', 'dict', 'set', 'tuple',
  'sum', 'min', 'max', 'abs', 'round', 'sorted', 'enumerate', 'zip', 'map', 'filter', 'open', 'type',
  'isinstance', 'super', 'any', 'all', 'reversed', 'chr', 'ord', 'divmod', 'pow', 'repr', 'self',
])

// comment | triple string | string | number | word
const TOKEN =
  /(#[^\n]*)|([rRbBfF]{0,2}(?:"""[\s\S]*?"""|'''[\s\S]*?'''))|([rRbBfF]{0,2}(?:"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'))|(\b\d[\d_]*\.?\d*(?:[eE][+-]?\d+)?\b)|(@?[A-Za-z_][A-Za-z0-9_]*)/g

/** Tiny, dependency-free Python highlighter (colours only; not a parser). */
export function highlightPython(code: string): React.ReactNode[] {
  const nodes: React.ReactNode[] = []
  let last = 0
  let key = 0
  let prevWord = ''
  for (const m of code.matchAll(TOKEN)) {
    const index = m.index ?? 0
    if (index > last) nodes.push(code.slice(last, index))
    const [text, comment, tripleStr, str, num, word] = m
    let cls = ''
    if (comment) cls = 'text-white/45 italic'
    else if (tripleStr || str) cls = 'text-[#FFB86B]'
    else if (num) cls = 'text-[#7EE2FF]'
    else if (word) {
      if (KEYWORDS.has(word)) cls = 'text-[#FF79C6] font-bold'
      else if (prevWord === 'def' || prevWord === 'class') cls = 'text-[#50FA7B]'
      else if (BUILTINS.has(word)) cls = 'text-[#8BE9FD]'
      else if (word.startsWith('@')) cls = 'text-[#F1FA8C]'
      prevWord = word
    }
    if (!word) prevWord = ''
    nodes.push(cls ? <span key={key++} className={cls}>{text}</span> : text)
    last = index + text.length
  }
  if (last < code.length) nodes.push(code.slice(last))
  return nodes
}
