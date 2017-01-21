import React from "react";
import {Route, IndexRedirect} from "react-router";
import Root from "./Root";
import EventsPageContainer from "../components/character/events/EventsPageContainer";
import CharacterPageContainer from "../components/character/CharacterPageContainer";
import PlayerPageContainer from "../components/player/PlayerPageContainer";
import DashboardContainer from "../components/player/DashboardContainer";
import EntitiesPageContainer from "../components/character/entities/EntitiesPageContainer";

const routes = (
  <Route path="/" component={Root}>
    <IndexRedirect to="player"/>
    <Route path="player" component={PlayerPageContainer}>
      <IndexRedirect to="dashboard"/>
      <Route path="dashboard" component={DashboardContainer}/>
    </Route>
    <Route path="character/:characterId" component={CharacterPageContainer}>
      <IndexRedirect to="events"/>
      <Route path="events" component={EventsPageContainer}/>
      <Route path="entities" component={EntitiesPageContainer}/>
    </Route>
  </Route>
);

export default routes;
