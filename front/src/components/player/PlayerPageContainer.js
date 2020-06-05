import {connect} from "react-redux";
import {fromPlayerState, getOwnCharactersList, requestOwnCharactersList} from "../../modules/player";
import React from "react";
import TopBarContainer from "./topBar/TopBarContainer";
import NotificationsContainer from "../commons/notifications/NotificationsContainer";

class PlayerPage extends React.Component {
  constructor(props) {
    super(props);
  }

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
        <TopBarContainer characterIdsList={this.props.characterIdsList} mainPageActive={true}/>
      </div>
      <br/><br/>
      {this.props.children}
      <NotificationsContainer characterId={null}/>
    </div>;
  }
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
