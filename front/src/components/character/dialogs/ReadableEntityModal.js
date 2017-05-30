import {Button, Modal} from "react-bootstrap";
import React from "react";


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
    return <Modal
      show={true}
      onHide={onCancelEdit}
      dialogClassName="ReadableEntityModal-dialog"
    >
      <Modal.Header>
        <Modal.Title>
          <input className="form-control" type="text" onChange={this.onTitleChange} value={this.state.title}/>
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <textarea className="form-control"
                  onChange={this.onContentsChange}
                  value={this.state.contents}
        />
      </Modal.Body>
      <Modal.Footer>
        <Button onClick={this.handleConfirmEdit}>Save</Button>
        <Button onClick={onCancelEdit}>Cancel</Button>
      </Modal.Footer>
    </Modal>;
  }
}


const ReadReadableModal = ({title, contents, editable, onClose, onClickEdit}) => {
  return <Modal
    show={true}
    onHide={onClose}
    dialogClassName="ReadableEntityModal-dialog"
  >
    <Modal.Header closeButton>
      <span>{editable ? <Button style={{float: "right"}} onClick={onClickEdit}>
        Edit
      </Button> : null}</span>
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
