import {connect} from "react-redux";
import TopBar from "./TopBar";
import {requestOwnCharactersList} from "./../player/actions";
import {getOwnCharactersList} from "./reducers";

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
