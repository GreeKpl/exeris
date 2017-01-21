import {connect} from "react-redux";
import Equipment from "./Equipment";

const mapStateToProps = (state, ownProps) => {
  return {characterId: ownProps.characterId};
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const EquipmentContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(Equipment);

export default EquipmentContainer;
