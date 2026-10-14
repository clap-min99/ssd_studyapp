import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { auth } from "../api/client";

export default function Account({ onDeleted }) {
  const [password, setPassword] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  async function handleDelete(event) {
    event.preventDefault();
    if (!confirmed || loading) return;
    setLoading(true);
    setError(null);
    try {
      await auth.deleteAccount(password);
      navigate("/", { replace: true });
      onDeleted();
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }

  return (
    <section>
      <h1>계정 관리</h1>
      <p>{auth.getUsername()}님의 계정</p>
      <h2>회원 탈퇴</h2>
      <p>계정과 복습 기록, 스트릭, 작성한 질문·인사이트가 삭제되며 복구할 수 없어요.</p>
      <p>공용 기사·용어·챕터·레슨은 유지돼요. 다시 가입해도 이전 개인 기록은 돌아오지 않아요.</p>
      <form className="login-form" onSubmit={handleDelete}>
        <label htmlFor="delete-password">현재 비밀번호</label>
        <input
          id="delete-password"
          className="search-input"
          type="password"
          autoComplete="current-password"
          required
          disabled={loading}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
        <label>
          <input
            type="checkbox"
            required
            disabled={loading}
            checked={confirmed}
            onChange={(event) => setConfirmed(event.target.checked)}
          />{" "}
          삭제되는 내용을 확인했으며, 계정을 영구 삭제하는 데 동의합니다.
        </label>
        {error && <p role="alert" className="status-message error">{error}</p>}
        <button className="btn-primary" type="submit" disabled={loading || !confirmed || !password}>
          {loading ? "계정 삭제 중..." : "계정 영구 삭제"}
        </button>
      </form>
    </section>
  );
}
