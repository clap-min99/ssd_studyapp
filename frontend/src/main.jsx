import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { marked } from 'marked'
import './index.css'
import App from './App.jsx'

// CommonMark 규칙상 "**FTL(...)**은"처럼 닫는 ** 앞이 문장부호이고 뒤에 조사가 붙으면
// 굵게가 안 먹는다. 한국어에선 흔해서 **...**는 무조건 굵게 처리한다 (앱 전체 marked에 적용).
marked.use({
  extensions: [{
    name: 'strong',
    level: 'inline',
    start: (src) => src.indexOf('**'),
    tokenizer(src) {
      const m = /^\*\*(?=\S)([\s\S]*?\S)\*\*/.exec(src)
      if (m) return { type: 'strong', raw: m[0], text: m[1], tokens: this.lexer.inlineTokens(m[1]) }
    },
  }],
})

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
