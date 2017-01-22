import {connect} from "react-redux";
import TopBar from "./TopBar";
import {getOwnCharactersList, fromPlayerState, requestOwnCharactersList} from "../../../modules/player";

const mapStateToProps = (state) => {
  return {
    charactersList: getOwnCharactersList(fromPlayerState(state)),
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
