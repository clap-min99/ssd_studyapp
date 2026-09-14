import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { termApi } from "../api/client";
import Modal from "./Modal";

const FAMILIARITY_LABEL = {
  new: "처음 봄",
  familiar: "익숙함",
  mastered: "설명 가능",
};

/** 용어 카드를 클릭했을 때 뜨는 상세 팝업.
 *  termId를 받아서 직접 상세 데이터를 불러온다 (목록에는 관련 기사 정보가 없어서). */
export default function TermDetail({ termId, onClose }) {
  const [term, setTerm] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    termApi
      .getDetail(termId)
      .then((data) => active && setTerm(data))
      .catch((e) => active && setError(e.message));
    return () => {
      active = false;
    };
  }, [termId]);

  return (
    <Modal onClose={onClose}>
      {error && <p className="status-message error">{error}</p>}
      {!term && !error && <p className="status-message">불러오는 중...</p>}

      {term && (
        <>
          <div className="term-card-header">
            <h3 style={{ fontSize: 20, margin: 0 }}>{term.term}</h3>
            <span className="pill pill-neutral">{FAMILIARITY_LABEL[term.familiarity]}</span>
          </div>

          <p style={{ marginTop: 14 }}>{term.meaning}</p>

          {term.relevance && (
            <div className="term-detail-block">
              <p className="term-detail-label">실제 어떻게 쓰이는지</p>
              <p>{term.relevance}</p>
            </div>
          )}

          <div className="term-detail-block">
            <p className="term-detail-label">
              이 개념이 나온 기사 ({term.appeared_in?.length ?? 0}건)
            </p>
            {term.appeared_in?.length ? (
              <ul className="term-appearance-list">
                {term.appeared_in.map((d) => (
                  <li key={d.id}>
                    <Link to={`/digest/${d.id}`} onClick={onClose}>
                      {d.date} · {d.subject}
                    </Link>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="status-message" style={{ margin: "8px 0" }}>
                기록된 기사가 없어요.
              </p>
            )}
          </div>
        </>
      )}
    </Modal>
  );
}
