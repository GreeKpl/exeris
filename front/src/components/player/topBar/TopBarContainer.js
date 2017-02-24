import {connect} from "react-redux";
import TopBar from "./TopBar";
import {getOwnCharactersList, fromPlayerState, requestOwnCharactersList} from "../../../modules/player";

const mapStateToProps = (state, ownProps) => {
  return {
    charactersList: getOwnCharactersList(fromPlayerState(state)),
    characterId: ownProps.characterId,
    mainPageActive: ownProps.mainPageActive,
  };
};

const mapDispatchToProps = (dispatch) => {
  return {
    requestState: () => {
      dispatch(requestOwnCharactersList());
    },
  };
};

const TopBarContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(TopBar);

export default TopBarContainer;
