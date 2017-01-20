import {connect} from "react-redux";
import TopBar from "./TopBar";
import {requestOwnCharactersList, getOwnCharactersList} from "../../modules/player";

const mapStateToProps = (state) => {
  return {
    charactersList: getOwnCharactersList(state),
  };
};

const mapDispatchToProps = (dispatch) => {
  return {
    onMount: () => dispatch(requestOwnCharactersList()),
  };
};

const TopBarContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(TopBar);

export default TopBarContainer;