export default function Privacy() {
  return (
    <div className="glossary">
      <h1>개인정보처리방침</h1>
      <p>
        이 애플리케이션은 개발자 본인의 학습 목적으로만 사용되는 개인 프로젝트입니다.
        Gmail API를 통해 본인 계정으로 수신된 다이제스트 메일만 읽기 전용으로 조회하며,
        수집된 다이제스트 메일 내용과 서술형 학습 답변은 구조화·해설·첨삭을 위해 OpenAI API로 전송됩니다.
      </p>
    </div>
  );
}
