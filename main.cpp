#include <iostream>
#include <fstream>
#include <vector>
#include <queue>
#include <random>
#include <algorithm>
#include <map>
using namespace std;

const map<string, double> weights {{"0", 0}, {"1", -4}, {"2", -3}, {"3", -2}, {"4", 5}, {"halfHeight", -0.5}, {"quarterHeight", -0.75}, {"deepsetGap", -3}, {"gaps", -0.5}};

enum Tetromino{
    I = 0,
    J = 1,
    L = 2,
    O = 3,
    S = 4,
    T = 5,
    Z = 6,
    NULLTETROMINO = 7
};

class Vector2Int{
    public:
        int x;
        int y;
    
    Vector2Int(int x, int y){
        this->x = x;
        this->y = y;
    }

    Vector2Int(){
        this->x = 0;
        this->y = 0;
    }

    Vector2Int operator+(const Vector2Int& other){
        return Vector2Int(this->x + other.x, this->y + other.y);
    }

    Vector2Int operator-(const Vector2Int& other){
        return Vector2Int(this->x - other.x, this->y - other.y);
    }

    // overload the << operator

    friend ostream& operator<<(ostream& os, const Vector2Int& vec){
        os << "(" << vec.x << ", " << vec.y << ")";
        return os;
    }

    friend bool operator==(const Vector2Int& vec1, const Vector2Int& vec2){
        return vec1.x == vec2.x && vec1.y == vec2.y;
    }
};

const Vector2Int spawnPosition = Vector2Int(4, 19); 
const int width = 10, height = 40;

vector<vector<Vector2Int>> Cells[8] = {
    // Tetromino.I
    {
        {Vector2Int(-1, 1), Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(2, 1)},
        {Vector2Int(1, -1), Vector2Int(1, 0), Vector2Int(1, 1), Vector2Int(1, 2)},
        {Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(2, 0)},
        {Vector2Int(0, -1), Vector2Int(0, 0), Vector2Int(0, 1), Vector2Int(0, 2)}
    },
    // Tetromino.J
    {
        {Vector2Int(-1, 1), Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0)},
        {Vector2Int(1, 1), Vector2Int(0, 1), Vector2Int(0, 0), Vector2Int(0, -1)},
        {Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(1, -1)},
        {Vector2Int(0, 1), Vector2Int(0, 0), Vector2Int(0, -1), Vector2Int(-1, -1)}
    },
    // Tetromino.L
    {
        {Vector2Int(1, 1), Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0)},
        {Vector2Int(1, -1), Vector2Int(0, -1), Vector2Int(0, 0), Vector2Int(0, 1)},
        {Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(-1, -1)},
        {Vector2Int(0, -1), Vector2Int(0, 0), Vector2Int(0, 1), Vector2Int(-1, 1)}
    },
    // Tetromino.O
    {
        {Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(0, 0), Vector2Int(1, 0)},
        {Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(0, 0), Vector2Int(1, 0)},
        {Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(0, 0), Vector2Int(1, 0)},
        {Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(0, 0), Vector2Int(1, 0)}
    },
    // Tetromino.S
    {
        {Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(-1, 0), Vector2Int(0, 0)},
        {Vector2Int(0, 1), Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(1, -1)},
        {Vector2Int(-1, -1), Vector2Int(0, -1), Vector2Int(0, 0), Vector2Int(1, 0)},
        {Vector2Int(-1, 1), Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(0, -1)}
    },
    // Tetromino.T
    {
        {Vector2Int(0, 1), Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0)},
        {Vector2Int(1, 0), Vector2Int(0, 0), Vector2Int(0, 1), Vector2Int(0, -1)},
        {Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(0, -1)},
        {Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(0, 1), Vector2Int(0, -1)}
    },
    // Tetromino.Z
    {
        {Vector2Int(-1, 1), Vector2Int(0, 1), Vector2Int(0, 0), Vector2Int(1, 0)},
        {Vector2Int(1, 1), Vector2Int(1, 0), Vector2Int(0, 0), Vector2Int(0, -1)},
        {Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(0, -1), Vector2Int(1, -1)},
        {Vector2Int(-1, -1), Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(0, 1)}
    }
};
vector<vector<Vector2Int>> WallKicksI = {
    {Vector2Int(0, 0), Vector2Int(-2, 0), Vector2Int(1, 0), Vector2Int(-2, -1), Vector2Int(1, 2)},
    {Vector2Int(0, 0), Vector2Int(-1, 0), Vector2Int(2, 0), Vector2Int(-1, 2), Vector2Int(2, -1)},
    {Vector2Int(0, 0), Vector2Int(2, 0), Vector2Int(-1, 0), Vector2Int(2, 1), Vector2Int(-1, -2)},
    {Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(-2, 0), Vector2Int(1, -2), Vector2Int(-2, 1)}
};
vector<vector<Vector2Int>> CounterWallKicksI = {
    {Vector2Int(0, 0), Vector2Int(-1, 0), Vector2Int(2, 0), Vector2Int(-1, 2), Vector2Int(2, -1)},
    {Vector2Int(0, 0), Vector2Int(2, 0), Vector2Int(-1, 0), Vector2Int(2, 1), Vector2Int(-1, -2)},
    {Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(-2, 0), Vector2Int(1, -2), Vector2Int(-2, 1)},
    {Vector2Int(0, 0), Vector2Int(-2, 0), Vector2Int(1, 0), Vector2Int(-2, -1), Vector2Int(1, 2)}
};
vector<vector<Vector2Int>> WallKicksJLOSTZ = {
    {Vector2Int(0, 0), Vector2Int(-1, 0), Vector2Int(-1, 1), Vector2Int(0, -2), Vector2Int(-1, -2)},
    {Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(1, -1), Vector2Int(0, 2), Vector2Int(1, 2)},
    {Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(1, 1), Vector2Int(0, -2), Vector2Int(1, -2)},
    {Vector2Int(0, 0), Vector2Int(-1, 0), Vector2Int(-1, -1), Vector2Int(0, 2), Vector2Int(-1, 2)}
};
vector<vector<Vector2Int>> CounterWallKicksJLOSTZ = {
    {Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(1, 1), Vector2Int(0, -2), Vector2Int(1, -2)},
    {Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(1, -1), Vector2Int(0, 2), Vector2Int(1, 2)},
    {Vector2Int(0, 0), Vector2Int(-1, 0), Vector2Int(-1, 1), Vector2Int(0, -2), Vector2Int(-1, -2)},
    {Vector2Int(0, 0), Vector2Int(-1, 0), Vector2Int(-1, -1), Vector2Int(0, 2), Vector2Int(-1, 2)}
};
vector<vector<Vector2Int>> Flips = {
    {Vector2Int(0, 0), Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(-1, 1), Vector2Int(1, 0), Vector2Int(-1, 0)},
    {Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(1, 2), Vector2Int(1, 1), Vector2Int(0, 2), Vector2Int(0, 1)},
    {Vector2Int(0, 0), Vector2Int(0, -1), Vector2Int(-1, -1), Vector2Int(1, -1), Vector2Int(-1, 0), Vector2Int(1, 0)},
    {Vector2Int(0, 0), Vector2Int(-1, 0), Vector2Int(-1, 2), Vector2Int(-1, 1), Vector2Int(0, 2), Vector2Int(0, 1)}
};

class Piece{
    public:
        Tetromino tetromino;
        Vector2Int position;
        int rotation;

        Piece(Tetromino tetromino, Vector2Int position, int rotation){
            this->tetromino = tetromino;
            this->position = position;
            this->rotation = rotation;
        }

        Piece(){
            this->tetromino = I;
            this->position = spawnPosition;
            this->rotation = 0;
        }

        void moveLeft(){
            this->position.x--;
        }

        void moveRight(){
            this->position.x++;
        }

        void moveDown(){
            this->position.y--;
        }

        void moveUp(){
            this->position.y++;
        }

        void rotateClockwise(){
            this->rotation = (this->rotation + 1) % 4;
        }

        void rotateCounterClockwise(){
            this->rotation = (this->rotation + 3) % 4;
        }

        void rotate180(){
            this->rotation = (this->rotation + 2) % 4;
        }
        
};

class Move{
    public:
        string type;
        Vector2Int offset;

        Move(string type, Vector2Int offset){
            this->type = type;
            this->offset = offset;
        }
        Move(string type){
            this->type = type;
            this->offset = Vector2Int(0,0);
        }
};


class Placement{
    public:
        Tetromino tetromino;
        Vector2Int position;
        int rotation;
        vector<Move> path;

        Placement(Tetromino tetromino, Vector2Int position, int rotation){
            this->tetromino = tetromino;
            this->position = position;
            this->rotation = rotation;
        }

        Placement(Tetromino tetromino, Vector2Int position, int rotation, vector<Move> path){
            this->tetromino = tetromino;
            this->position = position;
            this->rotation = rotation;
            this->path = path;
        }

        Placement(){
            this->tetromino = I;
            this->position = spawnPosition;
            this->rotation = 0;
        }

        void moveLeft(){
            this->position.x--;
        }

        void moveRight(){
            this->position.x++;
        }

        void moveDown(){
            this->position.y--;
        }

        void moveUp(){
            this->position.y++;
        }

        void rotateClockwise(){
            this->rotation = (this->rotation + 1) % 4;
        }

        void rotateCounterClockwise(){
            this->rotation = (this->rotation + 3) % 4;
        }

        void rotate180(){
            this->rotation = (this->rotation + 2) % 4;
        }
};

class Board{
    public:
        int width;
        int height;
        vector<vector<int>> board;

        Board(int width, int height){
            this->width = width;
            this->height = height;
            this->board = vector<vector<int>>(width, vector<int>(height, 0));
        }

        Board(){
            this->width = 10;
            this->height = 40;
            this->board = vector<vector<int>>(this->width, vector<int>(this->height, 0));
        }

       Board(int width, int height, vector<vector<int>> board){
            this->width = width;
            this->height = height;
            this->board = board;
       }

        double placePieceAndEvaluate(Placement placement){
            for(int i = 0; i < 4; i++){
                Vector2Int cell = placement.position + Cells[placement.tetromino][placement.rotation][i];
                this->board[cell.x][cell.y] = 1;
            }

            int score = 0;

            int maxHeight = this->maxHeight(), halfHeight = this->height / 2, quarterHeight = this->height / 4;

            int piecesPerColumn[this->width], deepestGap = 0;
            bool shouldClear[this->height];

            for(int i = 0; i < this->width; i++){
                piecesPerColumn[i] = 0;
            }

            for(int i = 0; i < this->height; i++){
                shouldClear[i] = true;
            }

            for (int y = maxHeight; y >= 0; y--) {
                for (int x = 0; x < this->width; x++) {
                    if (this->board[x][y] == 1) {

                        piecesPerColumn[x] += 1;
                        
                        if (y > halfHeight) {
                            score += weights.at("halfHeight");
                        }
                        else if (y > quarterHeight) {
                            score += weights.at("quarterHeight");
                        }
                    }
                    else{
                        deepestGap = max(deepestGap, piecesPerColumn[x]);

                        if(piecesPerColumn[x] > 0) {
                            score += weights.at("gaps");
                        }

                        shouldClear[y] = false;
                    }
                }
            }
            score += weights.at("deepsetGap") * deepestGap;

            // if piece is T and last move was a rotation, check for T-Spin

            if(placement.tetromino == Tetromino::T && (placement.path.back().type == "CW" || placement.path.back().type == "CCW")){
                
            }
            
            // clear lines
            int linesCleared = 0;
            for(int y = maxHeight; y > 0; y--){
                if(shouldClear[y]){
                    linesCleared++;
                    // remove line from board
                    board.erase(board.begin() + y);
                    // add new line to top
                    board.insert(board.begin(), vector<int>(this->width, 0));
                }
            }

            // add score for lines cleared
            score += weights.at(to_string(linesCleared));

            return score;
        }

        int maxHeight(){
            int maxHeight = 0;
            for(int x = 0; x < this->width; x++){
                for(int y = this->height - 1; y > 0 ; y--){
                    if(this->board[x][y] == 1){
                        maxHeight = max(maxHeight, y);
                        break;
                    }
                }
            }
            return maxHeight;
        }

        void removePiece(Piece piece){
            for(int i = 0; i < 4; i++){
                Vector2Int cell = piece.position + Cells[piece.tetromino][piece.rotation][i];
                this->board[cell.x][cell.y] = 0;
            }
        }

        friend ostream& operator<<(ostream& os, const Board& board){
            for(int y = board.height - 1; y >= 0; y--){
                for(int x = 0; x < board.width; x++){
                    os << board.board[x][y];
                }
                os << endl;
            }
            return os;
        }
};

class GameState{
    public:
        Board board;
        Tetromino piece;
        Tetromino heldPiece;
        queue<Tetromino> nextPieces;

        GameState(Board board, Tetromino piece, Tetromino heldPiece, queue<Tetromino> nextPieces){
            this->board = board;
            this->piece = piece;
            this->heldPiece = heldPiece;
            this->nextPieces = nextPieces;
        }

        GameState(){
            this->board = Board();
            this->piece = Tetromino::I;
            this->heldPiece = NULLTETROMINO;
            this->nextPieces = queue<Tetromino>();
        }

        bool isValid(Placement placement){
            for(int i = 0; i < 4; i++){
                Vector2Int cell = placement.position + Cells[placement.tetromino][placement.rotation][i];
                if(cell.x < 0 || cell.x >= this->board.width || cell.y < 0 || cell.y >= this->board.height){
                    return false;
                }
                if(this->board.board[cell.x][cell.y] == 1){
                    return false;
                }
            }
            return true;
        }

        bool isValid(Tetromino piece, Vector2Int position, int rotation){
            for(int i = 0; i < 4; i++){
                Vector2Int cell = position + Cells[piece][rotation][i];
                if(cell.x < 0 || cell.x >= this->board.width || cell.y < 0 || cell.y >= this->board.height){
                    return false;
                }
                if(this->board.board[cell.x][cell.y] == 1){
                    return false;
                }
            }
            return true;
        }

        vector<Placement> findPlacements(Tetromino piece, bool held = false){

            if(piece == NULLTETROMINO){
                cout << "Just tried to find placements for a null piece\n";
                return vector<Placement>();
            }
            
            
            // get max height on board
            int maxHeight = this->board.maxHeight();

            Vector2Int optimalSpawnPosition = Vector2Int(spawnPosition.x, min(spawnPosition.y, maxHeight + 3));

            vector<Move> path1;

            if(held){
                path1.push_back(Move("H", Vector2Int(0,0)));
            }
            
            for(int i = optimalSpawnPosition.y; i < spawnPosition.y; i++){
                path1.push_back(Move("S", Vector2Int(0,0)));
            }

            Placement start = Placement(piece, optimalSpawnPosition, 0, path1);
            vector<Placement> finalPlacements;

            cout << "Start: " << start.position << " " << start.rotation << "\n";

            const int borderOffset = 4;
            bool visited[4][width + borderOffset * 2][height + borderOffset * 2];

            for(int i = 0; i < 4; i++){
                for(int x = 0; x < width + borderOffset * 2; x++){
                    for(int y = 0; y < height + borderOffset * 2; y++){
                        visited[i][x][y] = false;
                    }
                }
            }

            queue<Placement> queue;
            queue.push(start);

            int whilecnt = 0;
            while(!queue.empty()){
                whilecnt++;
                auto currentPlacement = queue.front();
                queue.pop();

                if(visited[currentPlacement.rotation][currentPlacement.position.x + borderOffset][currentPlacement.position.y + borderOffset]){
                    continue;
                }

                visited[currentPlacement.rotation][currentPlacement.position.x + borderOffset][currentPlacement.position.y + borderOffset] = true;

                auto newPlacement = currentPlacement;
                // add to final placements if the piece cannot move down
                if(!isValid(piece, currentPlacement.position + Vector2Int(0,-1), currentPlacement.rotation)){
                    finalPlacements.push_back(currentPlacement);
                }
                else{ // move down if valid
                    newPlacement.moveDown();
                    newPlacement.path.push_back(Move("S", Vector2Int(0,0)));
                    queue.push(newPlacement);
                }
                
                newPlacement = currentPlacement;
                // move left
                if(isValid(piece, currentPlacement.position + Vector2Int(-1,0), currentPlacement.rotation)){
                    newPlacement.moveLeft();
                    newPlacement.path.push_back(Move("L", Vector2Int(0,0)));
                    queue.push(newPlacement);
                }

                newPlacement = currentPlacement;
                // move right
                if(isValid(piece, currentPlacement.position + Vector2Int(1,0), currentPlacement.rotation)){
                    newPlacement.moveRight();
                    newPlacement.path.push_back(Move("R", Vector2Int(0,0)));
                    queue.push(newPlacement);
                }

                // rotate clockwise
                newPlacement = currentPlacement;
                int newRotation = (currentPlacement.rotation + 1) % 4;
                vector<Vector2Int> newCells = Cells[piece][newRotation];

                vector<Vector2Int> offsetList;

                if(piece == Tetromino::I){
                    offsetList = WallKicksI[currentPlacement.rotation];
                }
                else{
                    offsetList = WallKicksJLOSTZ[currentPlacement.rotation];
                }

                for(auto offset : offsetList){
                    Vector2Int newPosition = currentPlacement.position + offset;  // Fix here
                    if(isValid(piece, newPosition, newRotation)){
                        newPlacement.position = newPosition;
                        newPlacement.rotation = newRotation;
                        newPlacement.path.push_back(Move("CW", offset));
                        queue.push(newPlacement);
                        break;
                    }
                }

                // rotate counter clockwise
                newPlacement = currentPlacement;
                newRotation = (currentPlacement.rotation + 3) % 4;
                newCells = Cells[piece][newRotation];

                if(piece == Tetromino::I){
                    offsetList = CounterWallKicksI[currentPlacement.rotation];
                }
                else{
                    offsetList = CounterWallKicksJLOSTZ[currentPlacement.rotation];
                }

                for(auto offset : offsetList){
                    Vector2Int newPosition = currentPlacement.position + offset;  // Fix here
                    if(isValid(piece, newPosition, newRotation)){
                        newPlacement.position = newPosition;
                        newPlacement.rotation = newRotation;
                        newPlacement.path.push_back(Move("CCW", offset));
                        queue.push(newPlacement);
                        break;
                    }
                }

                // rotate 180
                newPlacement = currentPlacement;
                newRotation = (currentPlacement.rotation + 2) % 4;
                newCells = Cells[piece][newRotation];

                for(auto offset : Flips[currentPlacement.rotation]){
                    newPlacement.position = currentPlacement.position + offset;
                    if(isValid(piece, newPlacement.position, newRotation)){
                        newPlacement.rotation = newRotation;
                        newPlacement.path.push_back(Move("180", offset));
                        queue.push(newPlacement);
                        break;
                    }
                }
            }
            cout << "While for: " << whilecnt << "\n";
            return finalPlacements;
        }

};

struct Node{
    double score;
    int depth;
    GameState gameState;
    Node* parent;
    vector<Node*> children;

    Node(double score, int depth, GameState gameState, Node* parent){
        this->depth = depth;
        this->gameState = gameState;
        this->parent = parent;
        this->score = score;
    }

    void generateChildren(){
        // clear children

        this->children.clear();

        if(this->gameState.nextPieces.empty()){
            return;
        }

        vector<Placement> placements = this->gameState.findPlacements(this->gameState.piece);

        for(auto placement : placements){
            auto newGameState = this->gameState;
            int eval = newGameState.board.placePieceAndEvaluate(placement);
            newGameState.piece = newGameState.nextPieces.front();
            newGameState.nextPieces.pop();
            this->children.push_back(new Node(eval, this->depth + 1, newGameState, this));
        }

        if(this->gameState.heldPiece == NULLTETROMINO){
            auto holdGameState = this->gameState;
            holdGameState.heldPiece = holdGameState.piece;
            holdGameState.piece = holdGameState.nextPieces.front();
            holdGameState.nextPieces.pop();
            placements = holdGameState.findPlacements(holdGameState.piece, true);

            for(auto placement : placements){
                auto newGameState = holdGameState;
                int eval = newGameState.board.placePieceAndEvaluate(placement);
                newGameState.piece = newGameState.nextPieces.front();
                newGameState.nextPieces.pop();
                this->children.push_back(new Node(eval, this->depth + 1, newGameState, this));
            }
            
        }
        else{
            auto holdGameState = this->gameState;
            auto temp = holdGameState.piece;
            holdGameState.piece = holdGameState.heldPiece;
            holdGameState.heldPiece = temp;
            placements = holdGameState.findPlacements(holdGameState.piece, true);

            for(auto placement : placements){
                auto newGameState = holdGameState;
                int eval = newGameState.board.placePieceAndEvaluate(placement);
                newGameState.piece = newGameState.nextPieces.front();
                newGameState.nextPieces.pop();
                this->children.push_back(new Node(eval, this->depth + 1, newGameState, this));
            }
        }
    }
};



int main()
{
    vector<Tetromino> defaultBag = {I, J, L, O, S, T, Z};
    random_device rd;
    mt19937 g(rd());
    queue<Tetromino> bigQueue;
    for(int i = 0; i < 1000; i++){
        auto newBag = defaultBag;
        shuffle(newBag.begin(), newBag.end(), g);
        for(auto tetromino : newBag){
            bigQueue.push(tetromino);
        }
    }
    Tetromino startPiece = bigQueue.front();
    cout << (Tetromino)startPiece << "\n";
    bigQueue.pop();

    GameState gameState = GameState(Board(width, height), startPiece, NULLTETROMINO, bigQueue); 
    
    Node* root = new Node(0, 0, gameState, NULL);

    root->generateChildren();

    for(auto child : root->children){
        cout << child->gameState.board << "\n" << child->score << "\n";
    }
    
    return 0;
}