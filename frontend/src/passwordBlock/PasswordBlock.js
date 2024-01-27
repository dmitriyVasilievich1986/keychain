import PasswordRow from "./PasswordRow";
import classNames from "classnames";
import React from "react";

function PasswordBlock(props) {
  if (!props.password?.fields) return null;

  const currentValues = props.password.fields.filter((p) => !p.is_deleted);
  const deletedValues = props.password.fields.filter((p) => p.is_deleted);

  return (
    <div className={classNames("passwordsBlock")}>
      <div>
        <h4>Current values:</h4>
        {currentValues
          .filter((p) => !p.is_deleted)
          .map((p, i) => (
            <PasswordRow key={`${p.name}_cur_${i}`} {...p} />
          ))}

        {deletedValues.length > 0 && (
          <h4 style={{ marginTop: "1rem" }}>Deleted values:</h4>
        )}
        {deletedValues
          .filter((p) => p.is_deleted)
          .map((p, i) => (
            <PasswordRow key={`${p.name}_hist_${i}`} {...p} />
          ))}
      </div>
    </div>
  );
}

export default PasswordBlock;
