import {connect} from "react-redux";
import {fromPlayerState, getOwnCharactersList, requestOwnCharactersList} from "../../modules/player";
import React from "react";
import NotificationsContainer from "../commons/notifications/NotificationsContainer";
import TopBarLayout from "../TopBarLayout";
import "./style.scss";
import CharacterDialogsContainer from "./dialogs/CharacterDialogsContainer";
import {IndexRedirect, Redirect, Route, Switch} from "react-router";
import EventsPageContainer from "./events/EventsPageContainer";
import EntitiesPageContainer from "./entities/EntitiesPageContainer";
import ActionsPageContainer from "./actions/ActionsPageContainer";
import OwnCharacterPageContainer from "./myCharacter/MyCharacterPageContainer";

class CharacterPage extends React.Component {
  componentDidMount() {
    if (this.props.characterIdsList.size === 0) {
      this.props.requestState();
    }
  }

  render() {
    return <div>
      <div style={{
        position: "fixed",
        top: "0px",
        left: "0px",
        right: "0px",
        zIndex: 1,
      }}>
        <TopBarLayout characterId={this.props.characterId}
                      characterIdsList={this.props.characterIdsList}
                      activePage={this.props.pageUrl}
                      characterActivePage={this.props.characterPageUrl}
                      isSmall={this.props.isSmall}
        />
      </div>
      <div className="CharacterPage-TopBarPlaceholder"/>
      <Switch>
        <Route path="/character/:characterId/events" component={EventsPageContainer}/>
        <Route path="/character/:characterId/entities" component={EntitiesPageContainer}/>
        <Route path="/character/:characterId/actions" component={ActionsPageContainer}/>
        <Route path="/character/:characterId/my-character" component={OwnCharacterPageContainer}/>
        <Route exact path="/character/:characterId"
               component={({location}) => <Redirect to={location.pathname + "/events"}/>}/>
      </Switch>
      <NotificationsContainer characterId={this.props.characterId}/>
      <CharacterDialogsContainer characterId={this.props.characterId}/>
    </div>;
  }
}

export {CharacterPage};


const mapStateToProps = (state, ownProps) => {
  console.log(state);
  console.log(ownProps);
  return {
    characterId: ownProps.match.params.characterId,
    characterIdsList: getOwnCharactersList(fromPlayerState(state)),
    characterPageUrl: /character\/\d+\/([^/]+)/.exec(ownProps.location.pathname)[1],
    isSmall: state.get("browser").atMost.small,
  };
};

const mapDispatchToProps = (dispatch) => {
  return {
    requestState: () => {
      dispatch(requestOwnCharactersList());
    },
  }
};

const CharacterPageContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CharacterPage);

export default CharacterPageContainer;
