(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([[2],{"91Qw":function(e,t,n){"use strict";n.r(t);var r=function(){function e(e,t){var n=this;this._modeId=e;this._defaults=t;this._worker=null;this._idleCheckInterval=setInterval(function(){return n._checkIfIdle()},30*1e3);this._lastUsedTime=0;this._configChangeListener=this._defaults.onDidChange(function(){return n._stopWorker()})}e.prototype._stopWorker=function(){if(this._worker){this._worker.dispose();this._worker=null}this._client=null};e.prototype.dispose=function(){clearInterval(this._idleCheckInterval);this._configChangeListener.dispose();this._stopWorker()};e.prototype._checkIfIdle=function(){if(!this._worker){return}var e=this._defaults.getWorkerMaxIdleTime();var t=Date.now()-this._lastUsedTime;if(e>0&&t>e){this._stopWorker()}};e.prototype._getClient=function(){var e=this;this._lastUsedTime=Date.now();if(!this._client){this._worker=monaco.editor.createWebWorker({moduleId:"vs/language/typescript/tsWorker",label:this._modeId,createData:{compilerOptions:this._defaults.getCompilerOptions(),extraLibs:this._defaults.getExtraLibs()}});var t=this._worker.getProxy();if(this._defaults.getEagerModelSync()){t=t.then(function(t){return e._worker.withSyncedResources(monaco.editor.getModels().filter(function(t){return t.getModeId()===e._modeId}).map(function(e){return e.uri}))})}this._client=t}return this._client};e.prototype.getLanguageServiceWorker=function(){var e=this;var t=[];for(var n=0;n<arguments.length;n++){t[n]=arguments[n]}var r;return this._getClient().then(function(e){r=e}).then(function(n){return e._worker.withSyncedResources(t)}).then(function(e){return r})};return e}();var o=undefined&&undefined.__extends||function(){var e=function(t,n){e=Object.setPrototypeOf||{__proto__:[]}instanceof Array&&function(e,t){e.__proto__=t}||function(e,t){for(var n in t)if(t.hasOwnProperty(n))e[n]=t[n]};return e(t,n)};return function(t,n){e(t,n);function r(){this.constructor=t}t.prototype=n===null?Object.create(n):(r.prototype=n.prototype,new r)}}();var i=monaco.Uri;var a=monaco.Promise;var s;(function(e){e[e["None"]=0]="None";e[e["Block"]=1]="Block";e[e["Smart"]=2]="Smart"})(s||(s={}));function u(e,t){if(typeof e==="string"){return e}else{var n=e;var r="";var o=0;while(n){if(o){r+=t;for(var i=0;i<o;i++){r+="  "}}r+=n.messageText;o++;n=n.next}return r}}function c(e){if(e){return e.map(function(e){return e.text}).join("")}return""}var l=function(){function e(e){this._worker=e}e.prototype._positionToOffset=function(e,t){var n=monaco.editor.getModel(e);return n.getOffsetAt(t)};e.prototype._offsetToPosition=function(e,t){var n=monaco.editor.getModel(e);return n.getPositionAt(t)};e.prototype._textSpanToRange=function(e,t){var n=this._offsetToPosition(e,t.start);var r=this._offsetToPosition(e,t.start+t.length);var o=n.lineNumber,i=n.column;var a=r.lineNumber,s=r.column;return{startLineNumber:o,startColumn:i,endLineNumber:a,endColumn:s}};return e}();var f=function(e){o(t,e);function t(t,n,r){var o=e.call(this,r)||this;o._defaults=t;o._selector=n;o._disposables=[];o._listener=Object.create(null);var i=function(e){if(e.getModeId()!==n){return}var t;var r=e.onDidChangeContent(function(){clearTimeout(t);t=setTimeout(function(){return o._doValidate(e.uri)},500)});o._listener[e.uri.toString()]={dispose:function(){r.dispose();clearTimeout(t)}};o._doValidate(e.uri)};var a=function(e){monaco.editor.setModelMarkers(e,o._selector,[]);var t=e.uri.toString();if(o._listener[t]){o._listener[t].dispose();delete o._listener[t]}};o._disposables.push(monaco.editor.onDidCreateModel(i));o._disposables.push(monaco.editor.onWillDisposeModel(a));o._disposables.push(monaco.editor.onDidChangeModelLanguage(function(e){a(e.model);i(e.model)}));o._disposables.push({dispose:function(){for(var e=0,t=monaco.editor.getModels();e<t.length;e++){var n=t[e];a(n)}}});o._disposables.push(o._defaults.onDidChange(function(){for(var e=0,t=monaco.editor.getModels();e<t.length;e++){var n=t[e];a(n);i(n)}}));monaco.editor.getModels().forEach(i);return o}t.prototype.dispose=function(){this._disposables.forEach(function(e){return e&&e.dispose()});this._disposables=[]};t.prototype._doValidate=function(e){var t=this;this._worker(e).then(function(n){if(!monaco.editor.getModel(e)){return null}var r=[];var o=t._defaults.getDiagnosticsOptions(),i=o.noSyntaxValidation,s=o.noSemanticValidation;if(!i){r.push(n.getSyntacticDiagnostics(e.toString()))}if(!s){r.push(n.getSemanticDiagnostics(e.toString()))}return a.join(r)}).then(function(n){if(!n||!monaco.editor.getModel(e)){return null}var r=n.reduce(function(e,t){return t.concat(e)},[]).map(function(n){return t._convertDiagnostics(e,n)});monaco.editor.setModelMarkers(monaco.editor.getModel(e),t._selector,r)}).then(undefined,function(e){console.error(e)})};t.prototype._convertDiagnostics=function(e,t){var n=this._offsetToPosition(e,t.start),r=n.lineNumber,o=n.column;var i=this._offsetToPosition(e,t.start+t.length),a=i.lineNumber,s=i.column;return{severity:monaco.MarkerSeverity.Error,startLineNumber:r,startColumn:o,endLineNumber:a,endColumn:s,message:u(t.messageText,"\n")}};return t}(l);var p=function(e){o(t,e);function t(){return e!==null&&e.apply(this,arguments)||this}Object.defineProperty(t.prototype,"triggerCharacters",{get:function(){return["."]},enumerable:true,configurable:true});t.prototype.provideCompletionItems=function(e,n,r,o){var i=e.getWordUntilPosition(n);var a=e.uri;var s=this._positionToOffset(a,n);return this._worker(a).then(function(e){return e.getCompletionsAtPosition(a.toString(),s)}).then(function(e){if(!e){return}var r=e.entries.map(function(e){return{uri:a,position:n,label:e.name,insertText:e.name,sortText:e.sortText,kind:t.convertKind(e.kind)}});return{suggestions:r}})};t.prototype.resolveCompletionItem=function(e,n,r,o){var i=this;var a=r;var s=a.uri;var u=a.position;return this._worker(s).then(function(e){return e.getCompletionEntryDetails(s.toString(),i._positionToOffset(s,u),a.label)}).then(function(e){if(!e){return a}return{uri:s,position:u,label:e.name,kind:t.convertKind(e.kind),detail:c(e.displayParts),documentation:{value:c(e.documentation)}}})};t.convertKind=function(e){switch(e){case y.primitiveType:case y.keyword:return monaco.languages.CompletionItemKind.Keyword;case y.variable:case y.localVariable:return monaco.languages.CompletionItemKind.Variable;case y.memberVariable:case y.memberGetAccessor:case y.memberSetAccessor:return monaco.languages.CompletionItemKind.Field;case y.function:case y.memberFunction:case y.constructSignature:case y.callSignature:case y.indexSignature:return monaco.languages.CompletionItemKind.Function;case y.enum:return monaco.languages.CompletionItemKind.Enum;case y.module:return monaco.languages.CompletionItemKind.Module;case y.class:return monaco.languages.CompletionItemKind.Class;case y.interface:return monaco.languages.CompletionItemKind.Interface;case y.warning:return monaco.languages.CompletionItemKind.File}return monaco.languages.CompletionItemKind.Property};return t}(l);var m=function(e){o(t,e);function t(){var t=e!==null&&e.apply(this,arguments)||this;t.signatureHelpTriggerCharacters=["(",","];return t}t.prototype.provideSignatureHelp=function(e,t,n){var r=this;var o=e.uri;return this._worker(o).then(function(e){return e.getSignatureHelpItems(o.toString(),r._positionToOffset(o,t))}).then(function(e){if(!e){return}var t={activeSignature:e.selectedItemIndex,activeParameter:e.argumentIndex,signatures:[]};e.items.forEach(function(e){var n={label:"",documentation:null,parameters:[]};n.label+=c(e.prefixDisplayParts);e.parameters.forEach(function(t,r,o){var i=c(t.displayParts);var a={label:i,documentation:c(t.documentation)};n.label+=i;n.parameters.push(a);if(r<o.length-1){n.label+=c(e.separatorDisplayParts)}});n.label+=c(e.suffixDisplayParts);t.signatures.push(n)});return t})};return t}(l);var g=function(e){o(t,e);function t(){return e!==null&&e.apply(this,arguments)||this}t.prototype.provideHover=function(e,t,n){var r=this;var o=e.uri;return this._worker(o).then(function(e){return e.getQuickInfoAtPosition(o.toString(),r._positionToOffset(o,t))}).then(function(e){if(!e){return}var t=c(e.documentation);var n=e.tags?e.tags.map(function(e){var t="*@"+e.name+"*";if(!e.text){return t}return t+(e.text.match(/\r\n|\n/g)?" \n"+e.text:" - "+e.text)}).join("  \n\n"):"";var i=c(e.displayParts);return{range:r._textSpanToRange(o,e.textSpan),contents:[{value:"```js\n"+i+"\n```\n"},{value:t+(n?"\n\n"+n:"")}]}})};return t}(l);var d=function(e){o(t,e);function t(){return e!==null&&e.apply(this,arguments)||this}t.prototype.provideDocumentHighlights=function(e,t,n){var r=this;var o=e.uri;return this._worker(o).then(function(e){return e.getOccurrencesAtPosition(o.toString(),r._positionToOffset(o,t))}).then(function(e){if(!e){return}return e.map(function(e){return{range:r._textSpanToRange(o,e.textSpan),kind:e.isWriteAccess?monaco.languages.DocumentHighlightKind.Write:monaco.languages.DocumentHighlightKind.Text}})})};return t}(l);var h=function(e){o(t,e);function t(){return e!==null&&e.apply(this,arguments)||this}t.prototype.provideDefinition=function(e,t,n){var r=this;var o=e.uri;return this._worker(o).then(function(e){return e.getDefinitionAtPosition(o.toString(),r._positionToOffset(o,t))}).then(function(e){if(!e){return}var t=[];for(var n=0,o=e;n<o.length;n++){var a=o[n];var s=i.parse(a.fileName);if(monaco.editor.getModel(s)){t.push({uri:s,range:r._textSpanToRange(s,a.textSpan)})}}return t})};return t}(l);var v=function(e){o(t,e);function t(){return e!==null&&e.apply(this,arguments)||this}t.prototype.provideReferences=function(e,t,n,r){var o=this;var a=e.uri;return this._worker(a).then(function(e){return e.getReferencesAtPosition(a.toString(),o._positionToOffset(a,t))}).then(function(e){if(!e){return}var t=[];for(var n=0,r=e;n<r.length;n++){var a=r[n];var s=i.parse(a.fileName);if(monaco.editor.getModel(s)){t.push({uri:s,range:o._textSpanToRange(s,a.textSpan)})}}return t})};return t}(l);var _=function(e){o(t,e);function t(){return e!==null&&e.apply(this,arguments)||this}t.prototype.provideDocumentSymbols=function(e,t){var n=this;var r=e.uri;return this._worker(r).then(function(e){return e.getNavigationBarItems(r.toString())}).then(function(e){if(!e){return}var t=function(e,o,i){var a={name:o.text,detail:"",kind:b[o.kind]||monaco.languages.SymbolKind.Variable,range:n._textSpanToRange(r,o.spans[0]),selectionRange:n._textSpanToRange(r,o.spans[0]),containerName:i};if(o.childItems&&o.childItems.length>0){for(var s=0,u=o.childItems;s<u.length;s++){var c=u[s];t(e,c,a.name)}}e.push(a)};var o=[];e.forEach(function(e){return t(o,e)});return o})};return t}(l);var y=function(){function e(){}e.unknown="";e.keyword="keyword";e.script="script";e.module="module";e.class="class";e.interface="interface";e.type="type";e.enum="enum";e.variable="var";e.localVariable="local var";e.function="function";e.localFunction="local function";e.memberFunction="method";e.memberGetAccessor="getter";e.memberSetAccessor="setter";e.memberVariable="property";e.constructorImplementation="constructor";e.callSignature="call";e.indexSignature="index";e.constructSignature="construct";e.parameter="parameter";e.typeParameter="type parameter";e.primitiveType="primitive type";e.label="label";e.alias="alias";e.const="const";e.let="let";e.warning="warning";return e}();var b=Object.create(null);b[y.module]=monaco.languages.SymbolKind.Module;b[y.class]=monaco.languages.SymbolKind.Class;b[y.enum]=monaco.languages.SymbolKind.Enum;b[y.interface]=monaco.languages.SymbolKind.Interface;b[y.memberFunction]=monaco.languages.SymbolKind.Method;b[y.memberVariable]=monaco.languages.SymbolKind.Property;b[y.memberGetAccessor]=monaco.languages.SymbolKind.Property;b[y.memberSetAccessor]=monaco.languages.SymbolKind.Property;b[y.variable]=monaco.languages.SymbolKind.Variable;b[y.const]=monaco.languages.SymbolKind.Variable;b[y.localVariable]=monaco.languages.SymbolKind.Variable;b[y.variable]=monaco.languages.SymbolKind.Variable;b[y.function]=monaco.languages.SymbolKind.Function;b[y.localFunction]=monaco.languages.SymbolKind.Function;var S=function(e){o(t,e);function t(){return e!==null&&e.apply(this,arguments)||this}t._convertOptions=function(e){return{ConvertTabsToSpaces:e.insertSpaces,TabSize:e.tabSize,IndentSize:e.tabSize,IndentStyle:s.Smart,NewLineCharacter:"\n",InsertSpaceAfterCommaDelimiter:true,InsertSpaceAfterSemicolonInForStatements:true,InsertSpaceBeforeAndAfterBinaryOperators:true,InsertSpaceAfterKeywordsInControlFlowStatements:true,InsertSpaceAfterFunctionKeywordForAnonymousFunctions:true,InsertSpaceAfterOpeningAndBeforeClosingNonemptyParenthesis:false,InsertSpaceAfterOpeningAndBeforeClosingNonemptyBrackets:false,InsertSpaceAfterOpeningAndBeforeClosingTemplateStringBraces:false,PlaceOpenBraceOnNewLineForControlBlocks:false,PlaceOpenBraceOnNewLineForFunctions:false}};t.prototype._convertTextChanges=function(e,t){return{text:t.newText,range:this._textSpanToRange(e,t.span)}};return t}(l);var w=function(e){o(t,e);function t(){return e!==null&&e.apply(this,arguments)||this}t.prototype.provideDocumentRangeFormattingEdits=function(e,t,n,r){var o=this;var i=e.uri;return this._worker(i).then(function(e){return e.getFormattingEditsForRange(i.toString(),o._positionToOffset(i,{lineNumber:t.startLineNumber,column:t.startColumn}),o._positionToOffset(i,{lineNumber:t.endLineNumber,column:t.endColumn}),S._convertOptions(n))}).then(function(e){if(e){return e.map(function(e){return o._convertTextChanges(i,e)})}})};return t}(S);var k=function(e){o(t,e);function t(){return e!==null&&e.apply(this,arguments)||this}Object.defineProperty(t.prototype,"autoFormatTriggerCharacters",{get:function(){return[";","}","\n"]},enumerable:true,configurable:true});t.prototype.provideOnTypeFormattingEdits=function(e,t,n,r,o){var i=this;var a=e.uri;return this._worker(a).then(function(e){return e.getFormattingEditsAfterKeystroke(a.toString(),i._positionToOffset(a,t),n,S._convertOptions(r))}).then(function(e){if(e){return e.map(function(e){return i._convertTextChanges(a,e)})}})};return t}(S);n.d(t,"setupTypeScript",function(){return C});n.d(t,"setupJavaScript",function(){return P});n.d(t,"getJavaScriptWorker",function(){return x});n.d(t,"getTypeScriptWorker",function(){return O});var T;var I;function C(e){I=K(e,"typescript")}function P(e){T=K(e,"javascript")}function x(){return new monaco.Promise(function(e,t){if(!T){return t("JavaScript not registered!")}e(T)})}function O(){return new monaco.Promise(function(e,t){if(!I){return t("TypeScript not registered!")}e(I)})}function K(e,t){var n=new r(t,e);var o=function(e){var t=[];for(var r=1;r<arguments.length;r++){t[r-1]=arguments[r]}return n.getLanguageServiceWorker.apply(n,[e].concat(t))};monaco.languages.registerCompletionItemProvider(t,new p(o));monaco.languages.registerSignatureHelpProvider(t,new m(o));monaco.languages.registerHoverProvider(t,new g(o));monaco.languages.registerDocumentHighlightProvider(t,new d(o));monaco.languages.registerDefinitionProvider(t,new h(o));monaco.languages.registerReferenceProvider(t,new v(o));monaco.languages.registerDocumentSymbolProvider(t,new _(o));monaco.languages.registerDocumentRangeFormattingEditProvider(t,new w(o));monaco.languages.registerOnTypeFormattingEditProvider(t,new k(o));new f(e,t,o);return o}}}]);