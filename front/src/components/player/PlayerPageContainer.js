import {connect} from "react-redux";
import PlayerPage from "./PlayerPage";
import {fromPlayerState, getOwnCharactersList, requestOwnCharactersList} from "../../modules/player";

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
