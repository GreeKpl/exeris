import {connect} from "react-redux";
import {fromPlayerState, getOwnCharactersList, requestOwnCharactersList} from "../../modules/player";
import React, {useEffect} from "react";
import TopBarContainer from "./topBar/TopBarContainer";
import NotificationsContainer from "../commons/notifications/NotificationsContainer";
import {Redirect, Route, Switch} from "react-router";
import DashboardContainer from "./DashboardContainer";

const PlayerPage = ({characterIdsList, requestState}) => {
  useEffect(() => {
    if (characterIdsList.size === 0) {
      requestState();
    }
  }, [characterIdsList, requestState]);

  return <div>
    <div style={{
      position: "fixed",
      top: "0px",
      left: "0px",
      right: "0px",
      zIndex: 1,
    }}>
      <TopBarContainer characterIdsList={characterIdsList} mainPageActive={true}/>
    </div>
    <br/><br/>
    <Switch>
      <Route exact path="/player/dashboard" component={DashboardContainer}/>
      <Redirect exact from="/player" to="/player/dashboard"/>
    </Switch>
    <NotificationsContainer characterId={null}/>
  </div>;
}

export {PlayerPage};

const mapStateToProps = (state, ownProps) => {
  return {
    characterIdsList: getOwnCharactersList(fromPlayerState(state)),
  };
};

const mapDispatchToProps = (dispatch) => {
  return {
    requestState: () => {
      dispatch(requestOwnCharactersList());
    },
  }
};

const PlayerPageContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(PlayerPage);

export default PlayerPageContainer;
