import {connect} from "react-redux";
import {getEntityInfo, fromEntitiesState} from "../../../modules/entities";
import {} from "../../../modules/entities-actionsAddon";
import {closeDetails, getDetailsTarget, fromDetailsState} from "../../../modules/details";
import {performEditReadableEntityAction} from "../../../modules/entities-actionsAddon";

import {Button, Modal} from "react-bootstrap";
import React from "react";
import "./style.scss";


class EditReadableModal extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      title: props.title,
      contents: props.rawContents,
    };

    this.onTitleChange = this.onTitleChange.bind(this);
    this.onContentsChange = this.onContentsChange.bind(this);
    this.handleConfirmEdit = this.handleConfirmEdit.bind(this);
  }

  handleConfirmEdit() {
    this.props.onConfirmEdit(this.state.title, this.state.contents);
  }

  onTitleChange(event) {
    const title = event.target.value;
    this.setState({
      title: title,
      contents: this.state.contents,
    });
  }

  onContentsChange(event) {
    const contents = event.target.value;
    this.setState({
      title: this.state.title,
      contents: contents,
    });
  }

  render() {
    const {onCancelEdit} = this.props;
    return <Modal show={true}
                  backdrop="static">
      <Modal.Header>
        <Modal.Title>
          <input className="form-control"
                 type="text"
                 onChange={this.onTitleChange}
                 value={this.state.title}/>
        </Modal.Title>
      </Modal.Header>
      <Modal.Body className="EditReadableModal-Body">
        <textarea className="form-control EditReadableModal-ContentsArea"
                  onChange={this.onContentsChange}
                  value={this.state.contents}/>
      </Modal.Body>
      <Modal.Footer>
        <Button onClick={this.handleConfirmEdit}>Save</Button>
        <Button onClick={onCancelEdit}>Cancel</Button>
      </Modal.Footer>
    </Modal>;
  }
}


const ReadReadableModal = ({title, contents, editable, onClose, onClickEdit}) => {
  return <Modal show={true}
                backdrop="static">
    <Modal.Header>
      <span className="ReadableEntityModal-Header-Toolbar">
        {editable && <Button onClick={onClickEdit}>
          Edit
        </Button>}
        <Button onClick={onClose}>
          Close
        </Button>
      </span>
      <Modal.Title>{title}</Modal.Title>
    </Modal.Header>
    <Modal.Body dangerouslySetInnerHTML={{__html: contents}}/>
  </Modal>;
};

export class ReadableEntityModal extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      isEdited: false,
    };

    this.handleClickEdit = this.handleClickEdit.bind(this);
    this.handleCancelEdit = this.handleCancelEdit.bind(this);
    this.handleConfirmEdit = this.handleConfirmEdit.bind(this);
  }

  handleClickEdit() {
    this.setState({
      isEdited: true,
    });
  }

  handleCancelEdit() {
    this.setState({
      isEdited: false,
    });
  }

  handleConfirmEdit(title, contents) {
    this.props.onConfirmEdit(title, contents);
    this.setState({
      isEdited: false,
    });
  }

  render() {
    const {title, contents, rawContents, editable, onClose} = this.props;

    if (this.state.isEdited) {
      return <EditReadableModal title={title}
                                contents={contents}
                                rawContents={rawContents}
                                editable={editable}
                                onConfirmEdit={this.handleConfirmEdit}
                                onCancelEdit={this.handleCancelEdit}/>;
    } else {
      return <ReadReadableModal title={title}
                                contents={contents}
                                editable={editable}
                                onClose={onClose}
                                onClickEdit={this.handleClickEdit}/>;
    }
  }
}


const mapStateToProps = (state, ownProps) => {
  const detailsTarget = getDetailsTarget(fromDetailsState(state, ownProps.characterId));
  const entityInfo = getEntityInfo(detailsTarget, fromEntitiesState(state, ownProps.characterId));
  return {
    characterId: ownProps.characterId,
    entityId: entityInfo.get("id", null),
    title: entityInfo.get("title", null),
    contents: entityInfo.get("contents", null),
    rawContents: entityInfo.get("rawContents", null),
    editable: entityInfo.get("textEditable", false),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onClose: () => {
      dispatch(closeDetails(ownProps.characterId));
    },
    onConfirmEdit: (title, contents) => {
      dispatch(performEditReadableEntityAction(ownProps.characterId, ownProps.entityId, title, contents));
    },
  };
};

export const ReadableEntityModalContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ReadableEntityModal);
