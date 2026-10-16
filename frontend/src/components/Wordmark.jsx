import "./Wordmark.css";

export default function Wordmark({ large = false }) {
  return (
    <img className={`wordmark${large ? " wordmark-large" : ""}`} src="/ssd-tech-log-logo-v2.png" alt="SSD Tech Log" width="2048" height="683" />
  );
}
