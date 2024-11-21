import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { useLocation, useParams } from "react-router-dom";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import Accordion from "@mui/material/Accordion";
import Container from "@mui/material/Container";
import Avatar from "@mui/material/Avatar";
import { FieldItem } from "./FieldItem";
import List from "@mui/material/List";
import Card from "@mui/material/Card";
import { AddField } from "./AddField";
import React from "react";
import axios from "axios";
import _ from "lodash";

export function Center() {
  const [password, setPassword] = React.useState(null);
  const location = useLocation();
  const params = useParams();

  React.useEffect(() => {
    if (!params.pk) return;
    axios
      .get(`/api/v1/password/${params.pk}`)
      .then((data) => {
        setPassword(data.data);
      })
      .catch((e) => {
        console.log(e);
      });
  }, [location.pathname]);

  const putFieldHandler = (id, value) => {
    axios
      .put(`/api/v1/field/${id}`, { password_id: params.pk, value })
      .then((data) => {
        setPassword((prev) => {
          const fields = [
            ...prev.result.fields.map((f) =>
              f.id === id ? { ...f, is_deleted: true } : f
            ),
            data.data.result,
          ];
          return { ...prev, result: { ...prev.result, fields } };
        });
      })
      .catch((e) => {
        console.log(e);
      });
  };

  const postFieldHandler = (name, value) => {
    axios
      .post(`/api/v1/field/`, {
        password_id: params.pk,
        value,
        name,
      })
      .then((data) => {
        setPassword((prev) => {
          const fields = [...prev.result.fields, data.data.result];
          return { ...prev, result: { ...prev.result, fields } };
        });
      })
      .catch((e) => {
        console.log(e);
      });
  };

  const deleteHandler = (id) => {
    axios
      .delete(`/api/v1/field/${id}`)
      .then(() => {
        setPassword((prev) => {
          const fields = prev.result.fields.map((f) =>
            f.id === id ? { ...f, is_deleted: true } : f
          );
          return { ...prev, result: { ...prev.result, fields } };
        });
      })
      .catch((e) => {
        console.log(e);
      });
  };

  if (!password) return null;
  const deletedArray = password.result.fields.filter((f) => f.is_deleted);
  return (
    <Container maxWidth="md" sx={{ mt: "1rem" }}>
      <Card>
        <CardHeader
          avatar={
            <Avatar aria-label="recipe">
              <img src={password.result.image_url} />
            </Avatar>
          }
          title={password.result.name}
          subheader={password.result.created_at}
        />
        <CardContent>
          <List>
            {password.result.fields
              .filter((f) => !f.is_deleted)
              .map((field) => (
                <FieldItem
                  deleteHandler={() => deleteHandler(field.id)}
                  putHandler={putFieldHandler}
                  key={field.id}
                  field={field}
                />
              ))}
            <AddField postHandler={postFieldHandler} />
          </List>
          {deletedArray.length > 0 && (
            <Accordion defaultExpanded>
              <AccordionSummary
                sx={{ backgroundColor: "#e5e5e5" }}
                expandIcon={<ExpandMoreIcon />}
                aria-controls="panel3-content"
                id="panel3-header"
              >
                Deleted
              </AccordionSummary>
              <AccordionDetails>
                <List>
                  {deletedArray.map((field) => (
                    <FieldItem key={field.id} field={field} />
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>
          )}
        </CardContent>
      </Card>
      <div style={{ height: "3rem" }} />
    </Container>
  );
}
