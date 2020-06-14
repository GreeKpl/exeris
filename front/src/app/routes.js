import React from "react";
import {Route, IndexRedirect} from "react-router";
import Root from "./Root";
import EventsPageContainer from "../components/character/events/EventsPageContainer";
import CharacterPageContainer from "../components/character/CharacterPageContainer";
import PlayerPageContainer from "../components/player/PlayerPageContainer";
import DashboardContainer from "../components/player/DashboardContainer";
import EntitiesPageContainer from "../components/character/entities/EntitiesPageContainer";
import ActionsPageContainer from "../components/character/actions/ActionsPageContainer";
import OwnCharacterPageContainer from "../components/character/myCharacter/MyCharacterPageContainer";
import AdminPageContainer from "../components/admin/AdminPageContainer";
import AdminDashboardContainer from "../components/admin/AdminDashboardContainer";
import EntityTypesManagementContainer from "../components/admin/entities/EntityTypesManagementContainer";
import LoginPageContainer from "../components/outer/LoginPageContainer/LoginPageContainer";

const routes = (
  <Route path="/" component={Root}>
    <Route path="login" component={LoginPageContainer}/>
    <IndexRedirect to="player"/>
    <Route path="player" component={PlayerPageContainer}>
      <IndexRedirect to="dashboard"/>
      <Route path="dashboard" component={DashboardContainer}/>
    </Route>
    <Route path="admin" component={AdminPageContainer}>
      <IndexRedirect to="dashboard"/>
      <Route path="dashboard" component={AdminDashboardContainer}/>
      <Route path="entityTypes" component={EntityTypesManagementContainer}/>
    </Route>
    <Route path="character/:characterId" component={CharacterPageContainer}>
      <IndexRedirect to="events"/>
      <Route path="events" component={EventsPageContainer}/>
      <Route path="entities" component={EntitiesPageContainer}/>
      <Route path="actions" component={ActionsPageContainer}/>
      <Route path="myCharacter" component={OwnCharacterPageContainer}/>
    </Route>
  </Route>
);

export default routes;
