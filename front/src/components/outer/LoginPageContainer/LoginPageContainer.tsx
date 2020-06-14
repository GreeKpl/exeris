import React, {SyntheticEvent, useState} from "react";
import {Button, ControlLabel, FormControl, FormGroup} from "react-bootstrap";
import {connect} from "react-redux";
import {login} from "../../../modules/session";
import {Dispatch} from "../../../store/types";
import {withRouter} from "react-router";
import {browserHistory} from 'react-router';

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
        <FormGroup controlId="email" bsSize="large">
          <ControlLabel>Email</ControlLabel>
          <FormControl
            autoFocus
            type="text"
            value={email}
            onChange={e => setEmail((e.target as HTMLTextAreaElement).value)} // TODO I hope new react-bootstrap does it better
          />
        </FormGroup>
        <FormGroup controlId="password" bsSize="large">
          <ControlLabel>Password</ControlLabel>
          <FormControl
            value={password}
            onChange={e => setPassword((e.target as HTMLTextAreaElement).value)} // TODO I hope new react-bootstrap does it better
            type="password"
          />
        </FormGroup>
        <Button block bsSize="large" type="submit">
          Login
        </Button>
      </form>
    </div>
  );
};

const mapStateToProps = () => ({});

const mapDispatchToProps = (dispatch: Dispatch) => ({
  onLogin: (email: string, password: string) => {
    dispatch(login(email, password, browserHistory));
  },
});

export default withRouter(connect(
  mapStateToProps,
  mapDispatchToProps,
)(LoginPageContainer));
