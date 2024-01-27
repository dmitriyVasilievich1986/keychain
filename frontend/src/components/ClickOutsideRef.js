import React from "react";

function ClickOutsideRef(props) {
  const objRef = React.useRef();

  React.useEffect(() => {
    function handleClickOutside(event) {
      if (objRef.current && !objRef.current.contains(event.target)) {
        props.clickHandler();
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [objRef]);

  return (
    <div
      className={props.className || ""}
      style={props.style || {}}
      ref={objRef}
    >
      {props.children}
    </div>
  );
}

export default ClickOutsideRef;
