import { useState } from "react";
import { auth } from "../api/client";

export default function Login({ onLoggedIn }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [signup, setSignup] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    if (signup && password !== passwordConfirm) {
      setError("비밀번호가 일치하지 않습니다.");
      return;
    }
    setLoading(true);
    try {
      if (signup) {
        await auth.signup(username, password, passwordConfirm);
      } else {
        await auth.login(username, password);
      }
      onLoggedIn();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-screen">
      <h1>SSD Tech Log</h1>
      <p className="feed-subject">{signup ? "계정을 만들고 학습을 시작하세요" : "개인 학습 기록 — 로그인이 필요해요"}</p>

      <form className="login-form" onSubmit={handleSubmit}>
        <input
          className="search-input"
          placeholder="아이디"
          aria-label="아이디"
          autoComplete="username"
          required
          maxLength={150}
          disabled={loading}
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoCapitalize="none"
          autoCorrect="off"
        />
        <input
          className="search-input"
          type="password"
          placeholder="비밀번호"
          aria-label="비밀번호"
          autoComplete={signup ? "new-password" : "current-password"}
          required
          maxLength={signup ? 128 : undefined}
          disabled={loading}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {signup && (
          <>
            <p className="feed-subject">아이디: 문자, 숫자, @ . + - _ 사용 가능. 비밀번호: 8자 이상, 아이디와 다른 조합 사용. 흔한 비밀번호와 숫자만으로 된 비밀번호는 사용할 수 없어요.</p>
            <input
              className="search-input"
              type="password"
              placeholder="비밀번호 확인"
              aria-label="비밀번호 확인"
              autoComplete="new-password"
              required
              maxLength={128}
              disabled={loading}
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
            />
          </>
        )}

        {error && <p role="alert" className="status-message error">{error}</p>}

        <button className="btn-primary" type="submit" disabled={loading}>
          {loading ? (signup ? "가입 중..." : "로그인 중...") : (signup ? "회원가입" : "로그인")}
        </button>
        <button
          className="logout-link"
          type="button"
          disabled={loading}
          onClick={() => {
            setSignup(!signup);
            setPassword("");
            setPasswordConfirm("");
            setError(null);
          }}
        >
          {signup ? "이미 계정이 있나요? 로그인" : "계정이 없나요? 회원가입"}
        </button>
      </form>
    </div>
  );
}
