#include <iostream>
#include <fstream>
#include <vector>
#include <queue>
#include <random>
#include <algorithm>
#include <map>
#include <chrono>
#include <deque>
#include <unordered_set>
#include <mutex>

using namespace std;

const map<string, double> weights{
    {"0", 0}, {"1", -4}, {"2", -3}, {"3", -1}, {"4", 3.5}, // normal line clears
    {"halfHeight", -2}, {"quarterHeight", -5}, {"gaps", -3.5}, {"height", -0.4}, {"covered", -0.2}, {"spikiness", -0.5}, // height and gaps
    {"TS0", 0}, {"TS1", 1}, {"TS2", 4}, {"TS3", 6}, {"TSm0", 0}, {"TSm1", -1.5}, {"TSm2", -1}
    }; // T-spins

enum Piece{
    I = 0,
    J = 1,
    L = 2,
    O = 3,
    S = 4,
    T = 5,
    Z = 6,
    NULLPIECE = 7
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
const int width = 10, height = 40, deathHeight = 22;

vector<vector<Vector2Int>> Cells[8] = {
    // Piece.I
    {
        {Vector2Int(-1, 1), Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(2, 1)},
        {Vector2Int(1, -1), Vector2Int(1, 0), Vector2Int(1, 1), Vector2Int(1, 2)},
        {Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(2, 0)},
        {Vector2Int(0, -1), Vector2Int(0, 0), Vector2Int(0, 1), Vector2Int(0, 2)}
    },
    // Piece.J
    {
        {Vector2Int(-1, 1), Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0)},
        {Vector2Int(1, 1), Vector2Int(0, 1), Vector2Int(0, 0), Vector2Int(0, -1)},
        {Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(1, -1)},
        {Vector2Int(0, 1), Vector2Int(0, 0), Vector2Int(0, -1), Vector2Int(-1, -1)}
    },
    // Piece.L
    {
        {Vector2Int(1, 1), Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0)},
        {Vector2Int(1, -1), Vector2Int(0, -1), Vector2Int(0, 0), Vector2Int(0, 1)},
        {Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(-1, -1)},
        {Vector2Int(0, -1), Vector2Int(0, 0), Vector2Int(0, 1), Vector2Int(-1, 1)}
    },
    // Piece.O
    {
        {Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(0, 0), Vector2Int(1, 0)},
        {Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(0, 0), Vector2Int(1, 0)},
        {Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(0, 0), Vector2Int(1, 0)},
        {Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(0, 0), Vector2Int(1, 0)}
    },
    // Piece.S
    {
        {Vector2Int(0, 1), Vector2Int(1, 1), Vector2Int(-1, 0), Vector2Int(0, 0)},
        {Vector2Int(0, 1), Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(1, -1)},
        {Vector2Int(-1, -1), Vector2Int(0, -1), Vector2Int(0, 0), Vector2Int(1, 0)},
        {Vector2Int(-1, 1), Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(0, -1)}
    },
    // Piece.T
    {
        {Vector2Int(0, 1), Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0)},
        {Vector2Int(1, 0), Vector2Int(0, 0), Vector2Int(0, 1), Vector2Int(0, -1)},
        {Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(1, 0), Vector2Int(0, -1)},
        {Vector2Int(-1, 0), Vector2Int(0, 0), Vector2Int(0, 1), Vector2Int(0, -1)}
    },
    // Piece.Z
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
vector<vector<Vector2Int>> TSpinFacingCorners = {
    {Vector2Int(-1, 1), Vector2Int(1, 1)},
    {Vector2Int(1, 1), Vector2Int(1, -1)},
    {Vector2Int(1, -1), Vector2Int(-1, -1)},
    {Vector2Int(-1, -1), Vector2Int(-1, 1)}
};
vector<Vector2Int> Diagonals = {
    Vector2Int(-1, 1),
    Vector2Int(1, 1),
    Vector2Int(1, -1),
    Vector2Int(-1, -1)
};

class Move{
    public:
        string type;
        int offset;

        Move(string type, int offset){
            this->type = type;
            this->offset = offset;
        }
        Move(string type){
            this->type = type;
            this->offset = 0;
        }
};


class Placement{
    public:
        Piece piece;
        Vector2Int position;
        int rotation;
        vector<Move> path;

        Placement(Piece piece, Vector2Int position, int rotation){
            this->piece = piece;
            this->position = position;
            this->rotation = rotation;
        }

        Placement(Piece piece, Vector2Int position, int rotation, vector<Move> path){
            this->piece = piece;
            this->position = position;
            this->rotation = rotation;
            this->path = path;
        }

        Placement(){
            this->piece = I;
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

        double placePieceAndEvaluate(Placement placement, Piece nextPiece){
            for(int i = 0; i < 4; i++){
                Vector2Int cell = placement.position + Cells[placement.piece][placement.rotation][i];
                this->board[cell.x][cell.y] = 1;
            }

            int score = 0;

            int maxHeight = this->maxHeight(), halfHeight = this->height / 2, quarterHeight = this->height / 4;
            
            score += weights.at("height") * maxHeight;

            // if maxheight >= deathheight, return -1000000
            if(maxHeight >= deathHeight){
                return -1000000;
            }

            bool shouldClear[this->height];

            for(int i = 0; i <= maxHeight; i++){
                shouldClear[i] = true;
            }

            for (int y = maxHeight; y >= 0; y--) {
                for (int x = 0; x < this->width; x++) {
                    if (this->board[x][y] == 0) {
                        shouldClear[y] = false;
                    }
                }
            }

            // if piece is T and last move was a rotation, check for T-Spin
            bool tspin = false, tspinmini = false;

            if(placement.piece == Piece::T && (placement.path.back().type == "CW" || placement.path.back().type == "CCW")){
                // check for fin and overhang T-spin : 
                if((placement.rotation == 2 || placement.rotation == 0) && placement.path.back().offset == 4){
                    tspin = true;
                }
                else{
                    // get number of corners filled
                    int cornersFilled = 0;
                    for(auto offset : Diagonals){
                        // if out of bounds, add to corners filled
                        if(placement.position.x + offset.x < 0 || placement.position.x + offset.x >= this->width || placement.position.y + offset.y < 0 || placement.position.y + offset.y >= this->height){
                            cornersFilled++;
                        }
                        else if(this->board[placement.position.x + offset.x][placement.position.y + offset.y] == 1){
                            cornersFilled++;
                        }
                    }

                    // get number of facing corners filled
                    int facingCornersFilled = 0;
                    for(auto offset : TSpinFacingCorners[placement.rotation]){
                        if(this->board[placement.position.x + offset.x][placement.position.y + offset.y] == 1){
                            facingCornersFilled++;
                        }
                    }

                    if(cornersFilled >= 3){
                        if(facingCornersFilled >= 2){
                            tspin = true;
                        }
                        else{
                            tspinmini = true;
                        }   
                    }
                }
            }
            
            // clear lines
            int linesCleared = 0;
            for(int y = maxHeight; y >= 0; y--){
                if(shouldClear[y]){
                    linesCleared++;
                    // move all lines above down
                    for(int i = y; i < this->height - 1; i++){
                        for(int x = 0; x < this->width; x++){
                            this->board[x][i] = this->board[x][i + 1];
                        }
                    }
                }
            }

            bool found1[width];
            for(int i = 0; i < width; i++){
                found1[i] = false;
            }

            for (int y = maxHeight - linesCleared; y >= 0; y--) {
                for (int x = 0; x < this->width; x++) {
                    if (this->board[x][y] == 1) {
                        found1[x] = true;
                        
                        if (y > halfHeight) {
                            score += weights.at("halfHeight");
                        }
                        else if (y > quarterHeight) {
                            score += weights.at("quarterHeight");
                        }
                    }
                    else{
                        if(found1[x]){
                            score += weights.at("gaps");
                        }
                    }
                }
            }

            int found0[width], cover = 0;
            for(int i = 0; i < width; i++){
                found0[i] = 0;
            }

            for(int y = 0; y < maxHeight - linesCleared; y++){
                for(int x = 0; x < this->width; x++){
                    if(this->board[x][y] == 0){
                        found0[x]++;
                    }
                    else{
                        cover += found0[x];
                    }
                }
            }

            score += weights.at("covered") * cover;

            int spikiness = 0, prev = 0;

            // prev is height of first column
            for(int y = 0; y < this->height; y++){
                if(this->board[0][y] == 1){
                    prev = y;
                    break;
                }
            }

            for(int x = 1; x < this->width; x++){
                int height = 0;
                for(int y = maxHeight; y >= 0; y--){
                    if(this->board[x][y] == 1){
                        height = y;
                        break;
                    }
                }
                spikiness += abs(height - prev) ;
                prev = height;
            }

            score += weights.at("spikiness") * spikiness;

            // if spawn of next piece is blocked, return -1000000
            for(int i = 0; i < 4; i++){
                Vector2Int cell = Vector2Int(spawnPosition.x, spawnPosition.y) + Cells[nextPiece][0][i];
                if(this->board[cell.x][cell.y] == 1){
                    return -1000000;
                }
            }

            if(tspin){
                score += weights.at("TS" + to_string(linesCleared));
            }
            else if (tspinmini){
                score += weights.at("TSm" + to_string(linesCleared));
            }

            else{
                score += weights.at(to_string(linesCleared));
            }

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

        friend ostream& operator<<(ostream& os, const Board& board){
            for(int y = board.height - 1; y >= 0; y--){
                for(int x = 0; x < board.width; x++){
                    if(board.board[x][y] == 1){
                        os << "#";
                    }
                    else{
                        os << "_";
                    }
                }
                os << endl;
            }
            return os;
        }
};

class GameState{
    public:
        Board board;
        Piece piece;
        Piece heldPiece;
        queue<Piece> nextPieces;

        GameState(Board board, Piece piece, Piece heldPiece, queue<Piece> nextPieces){
            this->board = board;
            this->piece = piece;
            this->heldPiece = heldPiece;
            this->nextPieces = nextPieces;
        }

        GameState(){
            this->board = Board();
            this->piece = Piece::I;
            this->heldPiece = NULLPIECE;
            this->nextPieces = queue<Piece>();
        }
        
        friend bool operator==(const GameState& gameState1, const GameState& gameState2){
            bool check1 = gameState1.board.board == gameState2.board.board && gameState1.piece == gameState2.piece && gameState1.heldPiece == gameState2.heldPiece;
            // check first 4 pieces in nextPieces
            bool check2 = true;
            for(int i = 0; i < 4; i++){
                if(gameState1.nextPieces.front() != gameState2.nextPieces.front()){
                    check2 = false;
                    break;
                }
            }
            return check1 && check2;
        }

        bool isValid(Placement placement){
            for(int i = 0; i < 4; i++){
                Vector2Int cell = placement.position + Cells[placement.piece][placement.rotation][i];
                if(cell.x < 0 || cell.x >= this->board.width || cell.y < 0 || cell.y >= this->board.height){
                    return false;
                }
                if(this->board.board[cell.x][cell.y] == 1){
                    return false;
                }
            }
            return true;
        }

        bool isValid(Piece piece, Vector2Int position, int rotation){
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

        vector<Placement> findPlacements(Piece piece, bool held = false){

            if(piece == NULLPIECE){
                cout << "Just tried to find placements for a null piece\n";
                return vector<Placement>();
            }
            
            
            // get max height on board
            int maxHeight = this->board.maxHeight();
            
            Vector2Int optimalSpawnPosition = Vector2Int(spawnPosition.x, min(spawnPosition.y, maxHeight + 3));

            vector<Move> path1;

            if(held){
                path1.push_back(Move("H", 0));
            }
            
            for(int i = optimalSpawnPosition.y; i < spawnPosition.y; i++){
                path1.push_back(Move("S", 0));
            }

            Placement start = Placement(piece, optimalSpawnPosition, 0, path1);
            vector<Placement> finalPlacements;

            // cout << "Start: " << start.position << " " << start.rotation << "\n";

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
                    newPlacement.path.push_back(Move("S", 0));
                    queue.push(newPlacement);
                }
                
                newPlacement = currentPlacement;
                // move left
                if(isValid(piece, currentPlacement.position + Vector2Int(-1,0), currentPlacement.rotation)){
                    newPlacement.moveLeft();
                    newPlacement.path.push_back(Move("L", 0));
                    queue.push(newPlacement);
                }

                newPlacement = currentPlacement;
                // move right
                if(isValid(piece, currentPlacement.position + Vector2Int(1,0), currentPlacement.rotation)){
                    newPlacement.moveRight();
                    newPlacement.path.push_back(Move("R", 0));
                    queue.push(newPlacement);
                }

                // rotate clockwise
                newPlacement = currentPlacement;
                int newRotation = (currentPlacement.rotation + 1) % 4;
                vector<Vector2Int> newCells = Cells[piece][newRotation];

                vector<Vector2Int> offsetList;

                if(piece == Piece::I){
                    offsetList = WallKicksI[currentPlacement.rotation];
                }
                else{
                    offsetList = WallKicksJLOSTZ[currentPlacement.rotation];
                }

                // for(auto offset : offsetList){
                //     Vector2Int newPosition = currentPlacement.position + offset;  // Fix here
                //     if(isValid(piece, newPosition, newRotation)){
                //         newPlacement.position = newPosition;
                //         newPlacement.rotation = newRotation;
                //         newPlacement.path.push_back(Move("CW", offset));
                //         queue.push(newPlacement);
                //         break;
                //     }
                // }

                // rewrite for loop to use index

                for(long long unsigned int i = 0; i < offsetList.size(); i++){
                    Vector2Int newPosition = currentPlacement.position + offsetList[i];
                    if(isValid(piece, newPosition, newRotation)){
                        newPlacement.position = newPosition;
                        newPlacement.rotation = newRotation;
                        newPlacement.path.push_back(Move("CW", i));
                        queue.push(newPlacement);
                        break;
                    }
                }

                // rotate counter clockwise
                newPlacement = currentPlacement;
                newRotation = (currentPlacement.rotation + 3) % 4;
                newCells = Cells[piece][newRotation];

                if(piece == Piece::I){
                    offsetList = CounterWallKicksI[currentPlacement.rotation];
                }
                else{
                    offsetList = CounterWallKicksJLOSTZ[currentPlacement.rotation];
                }

                // for(auto offset : offsetList){
                //     Vector2Int newPosition = currentPlacement.position + offset;  // Fix here
                //     if(isValid(piece, newPosition, newRotation)){
                //         newPlacement.position = newPosition;
                //         newPlacement.rotation = newRotation;
                //         newPlacement.path.push_back(Move("CCW", offset));
                //         queue.push(newPlacement);
                //         break;
                //     }
                // }

                for(long long unsigned int i = 0; i < offsetList.size(); i++){
                    Vector2Int newPosition = currentPlacement.position + offsetList[i];
                    if(isValid(piece, newPosition, newRotation)){
                        newPlacement.position = newPosition;
                        newPlacement.rotation = newRotation;
                        newPlacement.path.push_back(Move("CCW", i));
                        queue.push(newPlacement);
                        break;
                    }
                }

                // rotate 180
                newPlacement = currentPlacement;
                newRotation = (currentPlacement.rotation + 2) % 4;
                newCells = Cells[piece][newRotation];

                // for(auto offset : Flips[currentPlacement.rotation]){
                //     newPlacement.position = currentPlacement.position + offset;
                //     if(isValid(piece, newPlacement.position, newRotation)){
                //         newPlacement.rotation = newRotation;
                //         newPlacement.path.push_back(Move("180", offset));
                //         queue.push(newPlacement);
                //         break;
                //     }
                // }

                for(long long unsigned int i = 0; i < offsetList.size(); i++){
                    Vector2Int newPosition = currentPlacement.position + offsetList[i];
                    if(isValid(piece, newPosition, newRotation)){
                        newPlacement.position = newPosition;
                        newPlacement.rotation = newRotation;
                        newPlacement.path.push_back(Move("180", i));
                        queue.push(newPlacement);
                        break;
                    }
                }
            }
            // cout << "While for: " << whilecnt << "\n";
            return finalPlacements;
        }

};

template<>
struct std::hash<GameState>{
    size_t operator()(const GameState& gameState) const {
        size_t seed = 0;
        for(int x = 0; x < gameState.board.width; x++){
            for(int y = 0; y < gameState.board.height; y++){
                seed ^= gameState.board.board[x][y] + 0x9e3779b9 + (seed << 6) + (seed >> 2);
            }
        }
        seed ^= gameState.piece + 0x9e3779b9 + (seed << 6) + (seed >> 2);
        seed ^= gameState.heldPiece + 0x9e3779b9 + (seed << 6) + (seed >> 2);
        seed ^= gameState.nextPieces.front() + 0x9e3779b9 + (seed << 6) + (seed >> 2);
        return seed;
    }
};

int destructorCalls = 0;

struct Node {
    double score;
    int depth;
    GameState gameState;
    int parentIndex;
    vector<int> childIndexes;

    Node(double score, int depth, GameState gameState, int parentIndex){
        this->depth = depth;
        this->gameState = gameState;
        this->parentIndex = parentIndex;
        this->score = score;
    }

    // operator ==
    bool operator==(const Node& other){
        return this->gameState.board.board == other.gameState.board.board && this->gameState.piece == other.gameState.piece && this->gameState.heldPiece == other.gameState.heldPiece && this->gameState.nextPieces == other.gameState.nextPieces;
    }

    void generateChildren(int currentIndex);
};

vector<Node> nodes;
unordered_set<GameState> visitedStates;

void Node::generateChildren(int currentIndex){
    // clear children

    this->childIndexes.clear();

    if(this->gameState.nextPieces.empty()){
        return;
    }

    vector<Placement> placements = this->gameState.findPlacements(this->gameState.piece);

    for(auto placement : placements){
        auto newGameState = this->gameState;
        auto nextPiece = newGameState.nextPieces.front();
        // eval should add to score
        int eval = newGameState.board.placePieceAndEvaluate(placement, nextPiece) + this->score;
        newGameState.piece = nextPiece;
        newGameState.nextPieces.pop();
        nodes.push_back(Node(eval, this->depth + 1, newGameState, currentIndex));
        this->childIndexes.push_back(nodes.size() - 1);
    }

    if(this->gameState.heldPiece == NULLPIECE){
        auto holdGameState = this->gameState;
        holdGameState.heldPiece = holdGameState.piece;
        holdGameState.piece = holdGameState.nextPieces.front();
        holdGameState.nextPieces.pop();
        placements = holdGameState.findPlacements(holdGameState.piece, true);

        for(auto placement : placements){
            auto newGameState = holdGameState;
            auto nextPiece = newGameState.nextPieces.front();
            int eval = newGameState.board.placePieceAndEvaluate(placement, nextPiece) + this->score;
            newGameState.piece = nextPiece;
            newGameState.nextPieces.pop();
            nodes.push_back(Node(eval, this->depth + 1, newGameState,currentIndex));
            this->childIndexes.push_back(nodes.size() - 1);
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
            auto nextPiece = newGameState.nextPieces.front();
            int eval = newGameState.board.placePieceAndEvaluate(placement, nextPiece) + this->score;
            newGameState.piece = nextPiece;
            newGameState.nextPieces.pop();
            nodes.push_back(Node(eval, this->depth + 1, newGameState, currentIndex));
            this->childIndexes.push_back(nodes.size() - 1);
        }
    }
}

double bestScore = -10000000;
int bestNodeIndex;
mutex mutexForBestScore;

void updateBest(int newScore, int newNodeIndex) {
    lock_guard<mutex> lock(mutexForBestScore);
    
    if (newScore > bestScore) {
        bestScore = newScore;
        bestNodeIndex = newNodeIndex; 
    }
}

int main()
{
    vector<Piece> defaultBag = {I, J, L, O, S, T, Z};
    random_device rd;
    mt19937 g(rd());
    queue<Piece> bigQueue;
    for(int i = 0; i < 1000; i++){
        auto newBag = defaultBag;
        shuffle(newBag.begin(), newBag.end(), g);
        for(auto piece : newBag){
            bigQueue.push(piece);
        }
    }
    Piece startPiece = bigQueue.front();
    cout << (Piece)startPiece << "\n";
    bigQueue.pop();

    GameState gameState = GameState(Board(width, height), startPiece, NULLPIECE, bigQueue); 
    
    Node root = Node(0, 0, gameState, 0);

    nodes.push_back(root);

    // deque<int> queue;
    // lambda function to compare nodes from index
    auto cmp = [](int index1, int index2) { return nodes[index1].score < nodes[index2].score; };
    priority_queue<int, vector<int>, decltype(cmp)> queue(cmp);

    queue.push(0);

    while(true){
        // for 0.25 seconds, generate children recursively, using a BFS queue
        auto start = chrono::high_resolution_clock::now();
        bestScore = -10000000;
        int currentDepth = nodes[queue.top()].depth;
        int whilecnt = 0;
        while(!queue.empty()){
            whilecnt++;
            int currentIndex = queue.top();
            Node current = nodes[currentIndex];
            queue.pop();
            if(current.depth >= currentDepth + 5 || visitedStates.find(current.gameState) != visitedStates.end()){
                continue;
            }
            visitedStates.insert(current.gameState);
            // if eval of current node is better than best node, set best node to current node
            if(current.score > bestScore && current.depth != nodes[0].depth){
                updateBest(current.score, currentIndex);
            }

            current.generateChildren(currentIndex);

            for(auto childIndex : current.childIndexes){
                queue.push(childIndex);
            }

            auto end = chrono::high_resolution_clock::now();
            auto duration = chrono::duration_cast<chrono::milliseconds>(end - start);
            if(duration.count() > 334){ // 4 pieces per second
                break;
            }
        }
        cout << "While for: " << whilecnt << "\n";
        // while(bestNode->parent != root){
        //     bestNode = bestNode->parent;
        // }

        Node bestNode = nodes[bestNodeIndex];
        while(bestNode.parentIndex != 0){
            bestNode = nodes[bestNode.parentIndex];
        }

        // print best node
        cout << "Best node: " << bestNode.score << "\n";
        cout << "Depth: " << bestNode.depth << "\n";
        cout << "Board: " << "\n";
        cout << bestNode.gameState.board << "\n";
        
        // set queue for next step
        
        root = bestNode;
        root.score = 0;
        queue = priority_queue<int, vector<int>, decltype(cmp)>(cmp);
        queue.push(0);

        // clear nodes
        nodes.clear();
        nodes.push_back(root);

        visitedStates.clear();
        
    }
    
    
    return 0;
}