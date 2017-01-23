import {connect} from "react-redux";
import TopPanel from "./TopPanel";
import {
  getDetailsType,
  fromTopPanelState,
} from "../../../modules/topPanel";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    detailsType: getDetailsType(fromTopPanelState(state, ownProps.characterId)),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {}
};

const TopPanelContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(TopPanel);

export default TopPanelContainer;
