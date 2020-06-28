import React, {SyntheticEvent, useState} from "react";
import {Button, Form} from "react-bootstrap";
import {connect} from "react-redux";
import {login} from "../../../modules/session";
import {Dispatch} from "../../../store/types";
import {withRouter} from "react-router";

interface LoginPageContainerProps {
  onLogin: (email: string, password: string) => void;
}

const LoginPageContainer = ({onLogin}: LoginPageContainerProps) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault();
    onLogin(email, password);
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <Form.Group controlId="email">
          <Form.Label>Email</Form.Label>
          <Form.Control
            size="lg"
            autoFocus
            type="text"
            value={email}
            onChange={e => setEmail((e.target as HTMLTextAreaElement).value)} // TODO I hope new react-bootstrap does it better
          />
        </Form.Group>
        <Form.Group controlId="password">
          <Form.Label>Password</Form.Label>
          <Form.Control
            size="lg"
            value={password}
            onChange={e => setPassword((e.target as HTMLTextAreaElement).value)} // TODO I hope new react-bootstrap does it better
            type="password"
          />
        </Form.Group>
        <Button block size="lg" type="submit">
          Login
        </Button>
      </form>
    </div>
  );
};

const mapStateToProps = () => ({});

const mapDispatchToProps = (dispatch: Dispatch, ownProps: any) => ({
  onLogin: (email: string, password: string) => {
    dispatch(login(email, password, ownProps.history));
  },
});

export default withRouter(connect(
  mapStateToProps,
  mapDispatchToProps,
)(LoginPageContainer));
