import classNames from "classnames";
import React from "react";

function Message(props) {
  const [hidden, setHidden] = React.useState(true);

  React.useEffect(() => {
    setHidden(false);
    setInterval(() => {
      setHidden(true);
    }, 2000);
  }, [props.message]);

  return (
    <div
      className={classNames("messageWrapper", {
        hidden,
      })}
    >
      <div className={classNames({ error: props.type === "error" })}>
        {props.message}
      </div>
    </div>
  );
}

export default Message;
