import { InputRow } from "../components";
import classNames from "classnames";
import React from "react";

function PasswordBlock(props) {
  if (!props.password?.fields) return null;

  const currentValues = props.password.fields.filter((p) => !p.is_deleted);
  const deletedValues = props.password.fields.filter((p) => p.is_deleted);
  const secret = process.env.NODE_ENV === "development";

  return (
    <div className={classNames("passwordsBlock")}>
      <div>
        <h4>Current values:</h4>
        {currentValues.map((p, i) => (
          <InputRow secret={secret} key={`${i}_current`} copy={true} {...p} />
        ))}

        {deletedValues.length > 0 && (
          <h4 style={{ marginTop: "1rem" }}>Deleted values:</h4>
        )}
        {deletedValues.map((p, i) => (
          <InputRow secret={secret} key={`${i}_old`} copy={true} {...p} />
        ))}
      </div>
    </div>
  );
}

export default PasswordBlock;
