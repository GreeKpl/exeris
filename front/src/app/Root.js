import React from "react";
import {Redirect, Route, Switch, withRouter} from "react-router";
import LoginPageContainer from "../components/outer/LoginPageContainer/LoginPageContainer";
import PlayerPageContainer from "../components/player/PlayerPageContainer";
import AdminPageContainer from "../components/admin/AdminPageContainer";
import CharacterPageContainer from "../components/character/CharacterPageContainer";

const Root = () => {
  return <div style={{marginBottom: "200px"}}>
    <Switch>
      <Route path="/login" component={LoginPageContainer}/>
      <Route path="/player" component={PlayerPageContainer}/>
      <Route path="/admin" component={AdminPageContainer}/>
      <Route path="/character/:characterId" component={CharacterPageContainer}/>
      <Redirect exact from="/" to="/player"/>
    </Switch>
  </div>
};

export default withRouter(Root);
