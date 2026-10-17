import { useLayoutEffect, useRef } from "react";

export default function Modal({ onClose, children, label = "상세 보기" }) {
  const ref = useRef(null);
  useLayoutEffect(() => {
    const dialog = ref.current;
    const trigger = document.activeElement;
    dialog.showModal();
    return () => {
      dialog.close();
      if (trigger?.isConnected) trigger.focus();
    };
  }, []);

  return (
    <dialog ref={ref} className="modal-backdrop" aria-label={label} onCancel={(e) => { e.preventDefault(); onClose(); }} onClick={onClose}>
      <div className="modal-sheet" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose} aria-label="닫기">
          ×
        </button>
        {children}
      </div>
    </dialog>
  );
}
