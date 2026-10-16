import { useEffect, useState } from "react";
import "./LaunchScreen.css";
import Wordmark from "./Wordmark";

export default function LaunchScreen() {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timeout = window.setTimeout(() => setVisible(false), 1300);
    return () => window.clearTimeout(timeout);
  }, []);

  if (!visible) return null;

  return (
    <div className="launch-screen" aria-hidden="true">
      <div className="launch-brand">
        <Wordmark large />
        <div className="launch-signal"><span /><span /><span /></div>
      </div>
    </div>
  );
}
