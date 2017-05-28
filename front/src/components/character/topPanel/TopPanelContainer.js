import {connect} from "react-redux";
import TopPanel from "./TopPanel";
import {
  getDetailsType,
  fromDetailsState,
} from "../../../modules/details";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    detailsType: getDetailsType(fromDetailsState(state, ownProps.characterId)),
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
