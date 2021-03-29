import Rete from 'rete'
// import template from './nodeTemplate.js'
import { strSocket } from '../sockets.js'
import 'codemirror/mode/javascript/javascript.js'
import InputControl from '../controls/input'
import TextAreaControl from '../controls/text-area'

class ReteConverse extends Rete.Component {
  constructor () {
    super('Converse')
    // this.render = 'vue'
    // this.data.component = CustomNodeComponent;
    // this.data.props = {}
  }

  builder (node) {
    var input = new Rete.Input('input', 'String', strSocket, true)
    var output = new Rete.Output('output', 'String', strSocket, true)
    var controls = {
      'name': new InputControl('name', this.editor, 'converse'),
      'question': new InputControl('question', this.editor, 'question'),
      'pretext': new TextAreaControl('pretext', this.editor, 'answer'),
      'context_var': new InputControl('context_var', this.editor, 'context variable'),
      'transition': new InputControl('transition', this.editor, 'transition'),
      'pretext2': new InputControl('pretext2', this.editor, 'pretext for templated answer'),
      'template': new InputControl('template', this.editor, 'template'),
      'data': new TextAreaControl('data', this.editor, 'templated answer')

    }

    node.addInput(input).addOutput(output)
    for (var key in controls) {
      node.addControl(controls[key])
    }

    return node
  }
}

export default ReteConverse
