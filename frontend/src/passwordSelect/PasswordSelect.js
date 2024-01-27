import createIcon from "Images/add.png";
import update from "Images/pen.png";
import classNames from "classnames";
import React from "react";
import Item from "./Item";

function PasswordSelect(props) {
  const [hide, setHide] = React.useState(true);
  const selectWindowRef = React.useRef();

  React.useEffect(() => {
    function handleClickOutside(event) {
      if (
        selectWindowRef.current &&
        !selectWindowRef.current.contains(event.target)
      ) {
        setHide(true);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [selectWindowRef]);

  const clickHandler = (newID) => {
    setHide(true);
    props?.onChange && props.onChange(newID);
  };

  return (
    <div className={classNames("passwordSelectBlock")}>
      <div className={classNames("selectWrapper")} ref={selectWindowRef}>
        <div className={classNames("selectHead")}>
          <Item
            {...props.passwords.find((p) => p.id === props.value)}
            onClick={() => setHide((h) => !h)}
            selectedPassword={true}
          />
          <div className={classNames("selectButtons")}>
            <img src={update} />
            <img src={createIcon} onClick={props.createHandler} />
          </div>
        </div>
        <div className={classNames("list", { hide })}>
          {props.passwords
            .filter((p) => p.id !== props.value)
            .map((p) => (
              <Item onClick={clickHandler} key={p.id} {...p} />
            ))}
        </div>
      </div>
    </div>
  );
}

export default PasswordSelect;
