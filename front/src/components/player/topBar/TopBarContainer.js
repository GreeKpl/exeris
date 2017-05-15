import {connect} from "react-redux";
import TopBar from "./TopBar";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    characterIdsList: ownProps.characterIdsList,
    mainPageActive: ownProps.mainPageActive,
  };
};

const mapDispatchToProps = (dispatch) => {
  return {};
};

const TopBarContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(TopBar);

export default TopBarContainer;
